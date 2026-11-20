"""Pruebas de integración ejecutadas únicamente sobre PostgreSQL de pruebas aislado.
ADVERTENCIA: se borran/recrean tablas en la base de TEST_DATABASE_URL.
"""
import os
import pytest

URL = os.getenv('TEST_DATABASE_URL', '')
if not URL or not URL.startswith('postgresql+psycopg://') or '_test' not in URL:
    pytest.skip('Configura TEST_DATABASE_URL apuntando a PostgreSQL de pruebas (*_test)', allow_module_level=True)
os.environ['DATABASE_URL'] = URL
os.environ['DEMO_SEED'] = 'true'
os.environ['DEMO_PASSWORD'] = 'EcoConecta2026!'
from backend.database import Base, engine
from backend import models
Base.metadata.drop_all(bind=engine)
from fastapi.testclient import TestClient
from backend.main import app

PASSWORD='EcoConecta2026!'

def auth(client, email):
    res = client.post('/api/auth/login',json={'email':email,'password':PASSWORD})
    assert res.status_code==200, res.text
    return {'Authorization':'Bearer '+res.json()['token']}

def new_request(client,headers,kind):
    response=client.post('/api/requests',headers=headers,json={
        'waste_type':kind,'generator_type':'unidad_productiva',
        'address':'Carrera 10 # 20-30 Villas de San Pablo',
        'contact':'573001234567','preferred_schedule':'Mañana de 8 a 11',
        'notes':'Material separado y limpio'})
    assert response.status_code==201,response.text
    return response.json()

def test_full_pilot():
    with TestClient(app) as client:
        household=auth(client,'comercio@ecoconecta.demo')
        ch=auth(client,'coordinador.huerta@ecoconecta.demo')
        cr=auth(client,'coordinador.reciclaje@ecoconecta.demo')
        h=auth(client,'huertero@ecoconecta.demo')
        rec=auth(client,'reciclador@ecoconecta.demo')
        organic=new_request(client,household,'organico')
        recyclable=new_request(client,household,'reciclable')
        id1,id2=organic['id'],recyclable['id']
        assert organic['status']=='recibida'
        assert len(client.get('/api/requests',headers=ch).json())==1
        assert len(client.get('/api/requests',headers=cr).json())==1
        assert client.post(f'/api/requests/{id1}/review',headers=cr).status_code==403
        assert client.post(f'/api/requests/{id1}/complete',headers=h,json={'material_kg':2}).status_code==403
        assert client.post(f'/api/requests/{id1}/review',headers=ch).status_code==200
        collectors=client.get('/api/collectors',headers=ch).json()
        target=collectors[0]['id']
        assert client.post(f'/api/requests/{id1}/assign',headers=ch,json={'collector_id':target}).status_code==200
        assert client.post(f'/api/requests/{id1}/schedule',headers=ch,json={'scheduled_at':'2028-01-01T15:00:00-05:00'}).status_code==200
        completed=client.post(f'/api/requests/{id1}/complete',headers=h,json={'material_kg':3.5})
        assert completed.status_code==200,completed.text
        assert completed.json()['points_awarded']==35
        assert completed.json()['status']=='recolectada'
        assert len(completed.json()['history'])>=5
        assert client.post(f'/api/requests/{id1}/complete',headers=h,json={'material_kg':3.5}).status_code==409
        assert client.get('/api/me',headers=household).json()['points']==35
        assert client.post(f'/api/requests/{id2}/assign',headers=ch,json={'collector_id':target}).status_code==403
        assert client.get(f'/api/requests/{id1}',headers=rec).status_code==403
        # Recolección reciclable dirigida al equipo correcto
        target2=client.get('/api/collectors',headers=cr).json()[0]['id']
        assert client.post(f'/api/requests/{id2}/assign',headers=cr,json={'collector_id':target2}).status_code==200
        assert client.get('/api/stats',headers=household).json()['by_type']=={'organico':1,'reciclable':1}
        assert client.get('/api/notifications',headers=auth(client,'admin@ecoconecta.demo')).status_code==200

def test_reject_unauthorized_and_bad_inputs():
    with TestClient(app) as client:
        assert client.get('/api/requests').status_code==401
        r=client.post('/api/auth/register',json={'name':'Persona Prueba','email':'vecina@ecoconecta.demo','password':'12345678','phone':'3001234567'})
        assert r.status_code==409
        user=auth(client,'vecina@ecoconecta.demo')
        assert client.post('/api/requests',headers=user,json={'waste_type':'peligroso','generator_type':'hogar','address':'Casa', 'contact':'123','preferred_schedule':'hoy'}).status_code==422
