"""Canal exclusivo permitido por el reto: WhatsApp Business Cloud API.
Sin credenciales se registra un evento 'sin_configurar', nunca se afirma envío.
Para iniciar mensajes fuera de la ventana de servicio, Meta requiere plantillas aprobadas.
"""
import os, json
import urllib.request
from .models import MessageLog

def send_whatsapp(db, req, kind):
    token=os.getenv('WHATSAPP_ACCESS_TOKEN','')
    phone_id=os.getenv('WHATSAPP_PHONE_NUMBER_ID','')
    if not token or not phone_id:
        db.add(MessageLog(request_id=req.id,kind=kind,status='sin_configurar',detail='Sin credenciales de WhatsApp Cloud API; notificación disponible en la plataforma'))
        return
    # Plantilla previamente aprobada en Meta con dos variables: código y programación.
    template=os.getenv('WHATSAPP_TEMPLATE_NAME','')
    if not template:
        db.add(MessageLog(request_id=req.id,kind=kind,status='sin_plantilla',detail='Configurar WHATSAPP_TEMPLATE_NAME aprobada en Meta'))
        return
    destination=''.join(c for c in req.contact if c.isdigit())
    if len(destination)<10:
        db.add(MessageLog(request_id=req.id,kind=kind,status='numero_invalido',detail='Número debe incluir código de país'))
        return
    body={'messaging_product':'whatsapp','to':destination,'type':'template','template':{'name':template,'language':{'code':'es'},'components':[{'type':'body','parameters':[{'type':'text','text':req.code},{'type':'text','text':str(req.scheduled_at)}]}]}}
    graph=os.getenv('WHATSAPP_GRAPH_VERSION','v22.0')
    url=f'https://graph.facebook.com/{graph}/{phone_id}/messages'
    request=urllib.request.Request(url,data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(request,timeout=7) as response:
            response.read()
        db.add(MessageLog(request_id=req.id,kind=kind,status='enviado',detail='Meta aceptó la solicitud de envío'))
    except Exception as exc:
        db.add(MessageLog(request_id=req.id,kind=kind,status='error',detail=str(exc)[:300]))
