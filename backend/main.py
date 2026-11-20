import os, math, uuid
from datetime import timezone
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import Base, engine, get_db, SessionLocal
from .models import User, CollectionRequest, RequestEvent, PointEntry, PointRule, Article, MessageLog, SessionToken, now
from .schemas import Register, Login, NewRequest, Assign, Schedule, Complete, PointUpdate, ArticleInput
from .security import hash_password, verify_password, make_token, current_user, roles
from .messaging import send_whatsapp

COORD = {'organico': 'coord_huerteros', 'reciclable': 'coord_recicladores'}
COLLECTOR = {'organico': 'huertero', 'reciclable': 'reciclador'}
ROOT = Path(__file__).resolve().parent.parent

def seed(db):
    if not db.query(PointRule).first():
        db.add_all([PointRule(waste_type=t, points_per_kg=10, validated_by_fsd=False) for t in COORD])
    if not db.query(Article).first():
        db.add_all([
            Article(title='¿Qué va en los residuos orgánicos?',category='Separación',body='Cáscaras de frutas y verduras, restos vegetales y hojas limpias pueden aprovecharse mediante compostaje. Evita mezclar plástico, vidrio, pilas o residuos peligrosos.'),
            Article(title='Reciclaje: limpio, seco y separado',category='Reciclaje',body='Separa papel, cartón, plástico, vidrio y metales aprovechables. Procura que estén limpios y secos. Si tienes dudas, pregunta antes de entregarlos.'),
            Article(title='Huerta y economía circular',category='Huerta comunitaria',body='La materia orgánica bien separada puede convertirse en compost para cuidar los suelos y fortalecer la huerta comunitaria de Villas de San Pablo.'),
            Article(title='¿Cómo solicitar una recolección?',category='Ruta de atención',body='Registra tu solicitud, indica si es orgánica o reciclable y espera la programación. Un coordinador asignará a una persona responsable. Al finalizar se registrará el material recibido.'),
        ])
    if os.getenv('DEMO_SEED','false').lower() == 'true':
        password = os.getenv('DEMO_PASSWORD','')
        if len(password) < 8: raise RuntimeError('DEMO_PASSWORD debe tener al menos 8 caracteres')
        demo = [
            ('Vecina piloto','vecina@ecoconecta.demo','solicitante'),
            ('Comercio piloto','comercio@ecoconecta.demo','solicitante'),
            ('Coordinación huerta','coordinador.huerta@ecoconecta.demo','coord_huerteros'),
            ('Coordinación reciclaje','coordinador.reciclaje@ecoconecta.demo','coord_recicladores'),
            ('Huertera piloto','huertero@ecoconecta.demo','huertero'),
            ('Reciclador piloto','reciclador@ecoconecta.demo','reciclador'),
            ('Administración EcoConecta','admin@ecoconecta.demo','admin'),
        ]
        for name,email,role in demo:
            if not db.query(User).filter_by(email=email).first():
                db.add(User(name=name,email=email,phone='3000000000',password_hash=hash_password(password),role=role,is_pilot=True))
    db.commit()

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db: seed(db)
    yield

app = FastAPI(title='EcoConecta · API', version='1.0.0', lifespan=lifespan, docs_url='/api/docs', openapi_url='/api/openapi.json')
app.mount('/assets', StaticFiles(directory=str(ROOT/'frontend')), name='assets')

@app.get('/')
def home(): return FileResponse(ROOT/'frontend'/'index.html')

@app.get('/api/health')
def health(): return {'status':'ok','service':'EcoConecta'}

def public_user(user):
    return {'id':user.id,'name':user.name,'email':user.email,'phone':user.phone,'role':user.role,'is_pilot':user.is_pilot}

@app.post('/api/auth/register', status_code=201)
def register(data: Register, db:Session=Depends(get_db)):
    if db.query(User).filter_by(email=data.email).first(): raise HTTPException(409,'Correo ya registrado')
    user = User(name=data.name.strip(),email=data.email,phone=data.phone.strip(),password_hash=hash_password(data.password),role='solicitante',is_pilot=False)
    db.add(user); db.commit(); db.refresh(user)
    return {'token':make_token(db,user),'user':public_user(user)}

@app.post('/api/auth/login')
def login(data: Login,db:Session=Depends(get_db)):
    user=db.query(User).filter_by(email=data.email.lower().strip()).first()
    if not user or not verify_password(data.password,user.password_hash) or not user.active: raise HTTPException(401,'Credenciales incorrectas')
    return {'token':make_token(db,user),'user':public_user(user)}

@app.post('/api/auth/logout')
def logout(user:User=Depends(current_user),db:Session=Depends(get_db)):
    db.query(SessionToken).filter_by(user_id=user.id).delete()
    db.commit(); return {'ok':True}

@app.get('/api/me')
def me(user:User=Depends(current_user),db:Session=Depends(get_db)):
    points=db.query(func.coalesce(func.sum(PointEntry.points),0)).filter_by(user_id=user.id).scalar()
    return {**public_user(user),'points':int(points)}

@app.get('/api/articles')
def articles(db:Session=Depends(get_db)):
    return [{'id':a.id,'title':a.title,'category':a.category,'body':a.body} for a in db.query(Article).filter_by(published=True).order_by(Article.id).all()]

@app.post('/api/articles',status_code=201)
def add_article(data:ArticleInput,user:User=Depends(roles('admin')),db:Session=Depends(get_db)):
    article=Article(**data.model_dump());db.add(article);db.commit();return {'id':article.id}

def can_see(req,user):
    if user.role=='admin' or req.requester_id==user.id: return True
    if user.role in COORD.values(): return COORD[req.waste_type]==user.role
    if user.role in COLLECTOR.values(): return req.collector_id==user.id
    return False

def request_json(req, user, db, full=False):
    allowed = can_see(req,user)
    if not allowed: raise HTTPException(403,'Sin acceso a esta solicitud')
    obj={'id':req.id,'code':req.code,'requester_id':req.requester_id,'waste_type':req.waste_type,'generator_type':req.generator_type,
         'status':req.status,'preferred_schedule':req.preferred_schedule,'scheduled_at':req.scheduled_at,
         'coordinator_id':req.coordinator_id,'collector_id':req.collector_id,
         'collector_name':req.collector.name if req.collector else None,
         'material_kg':float(req.material_kg) if req.material_kg is not None else None,
         'points_awarded':req.points_awarded,'created_at':req.created_at}
    # Privacy: only request owner, assigned operational roles or admin can access contact and address
    operational = user.role=='admin' or user.id==req.requester_id or (user.role==COORD[req.waste_type]) or req.collector_id==user.id
    if operational: obj.update({'address':req.address,'contact':req.contact,'notes':req.notes,'requester_name':req.requester.name})
    if full:
        obj['history']=[{'action':e.action,'detail':e.detail,'at':e.created_at} for e in db.query(RequestEvent).filter_by(request_id=req.id).order_by(RequestEvent.id).all()]
    return obj

def record(db,req,user,action,detail=''):
    db.add(RequestEvent(request_id=req.id,actor_id=user.id,action=action,detail=detail))

@app.post('/api/requests',status_code=201)
def create_request(data:NewRequest,user:User=Depends(roles('solicitante','admin')),db:Session=Depends(get_db)):
    if os.getenv('PILOT_ONLY','false').lower()=='true' and not user.is_pilot and user.role!='admin':
        raise HTTPException(403,'El piloto está restringido a participantes habilitados')
    req=CollectionRequest(code='ECO-'+uuid.uuid4().hex[:9].upper(),requester_id=user.id,**data.model_dump())
    db.add(req);db.flush();record(db,req,user,'recibida','Solicitud creada y enrutada a '+COORD[req.waste_type]);db.commit();db.refresh(req)
    return request_json(req,user,db,True)

@app.get('/api/requests')
def list_requests(user:User=Depends(current_user),db:Session=Depends(get_db)):
    query=db.query(CollectionRequest)
    if user.role=='solicitante': query=query.filter_by(requester_id=user.id)
    elif user.role in COORD.values(): query=query.filter_by(waste_type='organico' if user.role=='coord_huerteros' else 'reciclable')
    elif user.role in COLLECTOR.values(): query=query.filter_by(collector_id=user.id)
    return [request_json(r,user,db) for r in query.order_by(CollectionRequest.created_at.desc()).limit(300).all()]

@app.get('/api/requests/{req_id}')
def get_request(req_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    req=db.get(CollectionRequest,req_id)
    if not req: raise HTTPException(404,'Solicitud no encontrada')
    return request_json(req,user,db,True)

@app.get('/api/collectors')
def collectors(user:User=Depends(roles('coord_huerteros','coord_recicladores','admin')),db:Session=Depends(get_db)):
    target=COLLECTOR['organico'] if user.role=='coord_huerteros' else COLLECTOR['reciclable'] if user.role=='coord_recicladores' else None
    query=db.query(User).filter_by(active=True)
    if target:query=query.filter_by(role=target)
    else:query=query.filter(User.role.in_(list(COLLECTOR.values())))
    return [public_user(u) for u in query.all()]

def coordinator_of(req,user):
    if user.role not in (COORD[req.waste_type],'admin'): raise HTTPException(403,'Corresponde al otro colectivo')

def changeable(req):
    if req.status in ('recolectada','cancelada'): raise HTTPException(409,'Esta solicitud ya está cerrada')

@app.post('/api/requests/{req_id}/review')
def review(req_id:int,user:User=Depends(roles('coord_huerteros','coord_recicladores','admin')),db:Session=Depends(get_db)):
    req=db.get(CollectionRequest,req_id)
    if not req: raise HTTPException(404)
    coordinator_of(req,user);changeable(req)
    req.coordinator_id=user.id;req.status='en_revision';record(db,req,user,'en_revision');db.commit()
    return request_json(req,user,db,True)

@app.post('/api/requests/{req_id}/assign')
def assign(req_id:int,data:Assign,user:User=Depends(roles('coord_huerteros','coord_recicladores','admin')),db:Session=Depends(get_db)):
    req=db.get(CollectionRequest,req_id)
    if not req:raise HTTPException(404)
    coordinator_of(req,user);changeable(req)
    collector=db.get(User,data.collector_id)
    if not collector or collector.role!=COLLECTOR[req.waste_type] or not collector.active: raise HTTPException(422,'El recolector no pertenece al colectivo requerido')
    req.coordinator_id=user.id;req.collector_id=collector.id;req.scheduled_at=None;req.status='asignada'
    record(db,req,user,'asignada',f'Responsable: {collector.name}');db.commit()
    return request_json(req,user,db,True)

@app.post('/api/requests/{req_id}/schedule')
def schedule(req_id:int,data:Schedule,user:User=Depends(current_user),db:Session=Depends(get_db)):
    req=db.get(CollectionRequest,req_id)
    if not req:raise HTTPException(404)
    changeable(req)
    if user.role not in ('admin',COORD[req.waste_type]) and user.id!=req.collector_id:raise HTTPException(403)
    if not req.collector_id or not req.coordinator_id:raise HTTPException(409,'Primero se requiere coordinador y recolector')
    dt=data.scheduled_at
    if dt.tzinfo is None: raise HTTPException(422,'Indica zona horaria para la fecha')
    if dt.astimezone(timezone.utc) <= now(): raise HTTPException(422,'La programación debe ser futura')
    req.scheduled_at=dt;req.status='programada';record(db,req,user,'programada',f'Fecha y hora: {dt.isoformat()}, responsable: {req.collector.name}')
    db.commit();send_whatsapp(db,req,'programacion');db.commit()
    return request_json(req,user,db,True)

@app.post('/api/requests/{req_id}/complete')
def complete(req_id:int,data:Complete,user:User=Depends(current_user),db:Session=Depends(get_db)):
    req=db.get(CollectionRequest,req_id)
    if not req:raise HTTPException(404)
    if user.id!=req.collector_id and user.role!='admin':raise HTTPException(403,'Solo la persona asignada puede cerrar la recolección')
    if req.status!='programada':raise HTTPException(409,'Solo se puede cerrar una solicitud programada')
    rule=db.query(PointRule).filter_by(waste_type=req.waste_type).first()
    if not rule:raise HTTPException(500,'Falta regla de puntos')
    points=math.floor(data.material_kg*rule.points_per_kg)
    req.material_kg=data.material_kg;req.points_awarded=points;req.status='recolectada'
    db.add(PointEntry(request_id=req.id,user_id=req.requester_id,points=points,formula=f'{data.material_kg} kg × {rule.points_per_kg} puntos/kg (regla piloto, no oficial)'))
    record(db,req,user,'recolectada',f'{data.material_kg} kg; {points} puntos; regla piloto no validada por FSD')
    db.commit();return request_json(req,user,db,True)

@app.post('/api/requests/{req_id}/cancel')
def cancel(req_id:int,user:User=Depends(current_user),db:Session=Depends(get_db)):
    req=db.get(CollectionRequest,req_id)
    if not req:raise HTTPException(404)
    if user.role!='admin' and user.id!=req.requester_id and user.role!=COORD[req.waste_type]:raise HTTPException(403)
    changeable(req);req.status='cancelada';record(db,req,user,'cancelada');db.commit()
    return request_json(req,user,db,True)

@app.get('/api/rules')
def rules(user:User=Depends(current_user),db:Session=Depends(get_db)):
    return [{'waste_type':r.waste_type,'points_per_kg':r.points_per_kg,'validated_by_fsd':r.validated_by_fsd} for r in db.query(PointRule).all()]

@app.put('/api/rules/{waste_type}')
def update_rule(waste_type:str,data:PointUpdate,user:User=Depends(roles('admin')),db:Session=Depends(get_db)):
    rule=db.query(PointRule).filter_by(waste_type=waste_type).first()
    if not rule:raise HTTPException(404)
    rule.points_per_kg=data.points_per_kg;rule.validated_by_fsd=False;db.commit()
    return {'ok':True,'notice':'Regla configurada localmente; pendiente de validación FSD'}

@app.get('/api/stats')
def stats(user:User=Depends(current_user),db:Session=Depends(get_db)):
    reqs=db.query(CollectionRequest).all()
    visible=[r for r in reqs if can_see(r,user)]
    return {'total':len(visible),'by_status':{s:sum(r.status==s for r in visible) for s in ['recibida','en_revision','asignada','programada','recolectada','cancelada']},'by_type':{t:sum(r.waste_type==t for r in visible) for t in COORD},'total_kg':round(sum(float(r.material_kg or 0) for r in visible),2),'total_points':sum(r.points_awarded for r in visible)}

@app.get('/api/admin/users')
def users(user:User=Depends(roles('admin')),db:Session=Depends(get_db)):
    return [public_user(u) for u in db.query(User).all()]

@app.put('/api/admin/users/{id}/pilot')
def pilot(id:int,enabled:bool,user:User=Depends(roles('admin')),db:Session=Depends(get_db)):
    target=db.get(User,id)
    if not target:raise HTTPException(404)
    target.is_pilot=enabled;db.commit();return {'ok':True}

@app.get('/api/notifications')
def notifications(user:User=Depends(roles('admin')),db:Session=Depends(get_db)):
    return [{'id':m.id,'request_id':m.request_id,'kind':m.kind,'status':m.status,'detail':m.detail} for m in db.query(MessageLog).order_by(MessageLog.id.desc()).limit(100)]
