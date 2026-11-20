# EcoConecta · Villas de San Pablo

MVP web para coordinar la separación y recolección de residuos orgánicos y reciclables en Villas de San Pablo, Barranquilla. Desarrollado de acuerdo con el reto oficial de la Hackathon Universidad Libre / Fundación Santo Domingo, 20–21 de noviembre de 2026.

## Funciones

Educación ambiental, registro de solicitudes desde hogares y unidades productivas, separación automática del flujo orgánico/reciclable, bandejas por colectivo, asignación de persona, programación de día/hora, historial consultable, cierre y puntos piloto, panel de indicadores, administración de contenidos y usuarios piloto. Incluye integración con WhatsApp Business Cloud API activable con credenciales propias.

## Requisitos

1. Docker Desktop (con Docker Compose) y Git. VS Code recomendado.
2. Al menos 2 GB de memoria disponible para los contenedores.
3. Puerto local 8000 libre.

## Instalación Windows / Mac / Linux

```bash
git clone URL_DEL_REPOSITORIO.git
cd ecoconecta
cp .env.example .env
# En Windows PowerShell: Copy-Item .env.example .env
# Editar .env: DEMO_PASSWORD y POSTGRES_PASSWORD
# IMPORTANTE: si se cambia POSTGRES_PASSWORD también cambiar la contraseña en DATABASE_URL

docker compose up --build -d
```

Abrir **http://localhost:8000**. API interactiva: **http://localhost:8000/api/docs**. Comprobar servicio: **http://localhost:8000/api/health**.

> Nota: `.env.example` trae credenciales locales de demostración. **No se deben utilizar en internet.** Para la nube establecer contraseñas aleatorias fuertes, `DEMO_SEED=false` y configurar cuentas operativas por un mecanismo administrativo seguro antes del piloto.

**Atajo sin Git:** descomprimir el ZIP, abrir la carpeta raíz con VS Code, copiar `.env.example` a `.env`, luego ejecutar `docker compose up --build -d` desde la terminal de esa carpeta.

## Cuentas ficticias de la demostración

Están disponibles cuando `DEMO_SEED=true`; todas utilizan la contraseña definida por `DEMO_PASSWORD` en `.env`.

| Rol | Correo |
|---|---|
| Hogar | vecina@ecoconecta.demo |
| Unidad productiva | comercio@ecoconecta.demo |
| Coordinador de huerteros | coordinador.huerta@ecoconecta.demo |
| Coordinador de recicladores | coordinador.reciclaje@ecoconecta.demo |
| Huertero | huertero@ecoconecta.demo |
| Reciclador | reciclador@ecoconecta.demo |
| Administrador | admin@ecoconecta.demo |

## Estructura de carpetas

```text
ecoconecta/
├── backend/
│   ├── main.py             # API REST, lógica y roles
│   ├── database.py         # conexión PostgreSQL
│   ├── models.py           # tablas y relaciones
│   ├── schemas.py          # validaciones de formularios
│   ├── security.py         # contraseñas y sesiones
│   └── messaging.py        # WhatsApp Business Cloud API
├── frontend/
│   ├── index.html          # estructura de la web
│   ├── css/styles.css      # estilo responsive
│   └── js/
│       ├── api.js          # conexión con backend
│       └── app.js          # navegación e interfaz
├── docs/
│   ├── ANALISIS_RETO.md    # requisitos y aceptación
│   ├── ARQUITECTURA.md     # componentes y datos
│   ├── DEMO_JURADO.md      # demo extremo a extremo
│   └── PUBLICACION.md      # GitHub y nube
├── tests/                  # pruebas de integración
├── .env.example            # variables sin secretos reales
├── Dockerfile              # imagen de la aplicación
├── docker-compose.yml      # API y PostgreSQL
└── requirements.txt        # dependencias Python
```

## Variables de entorno

| Variable | Uso |
|---|---|
| `DATABASE_URL` | URL privada de PostgreSQL para SQLAlchemy |
| `POSTGRES_PASSWORD` | Contraseña del contenedor PostgreSQL (definir en `.env`) |
| `DEMO_SEED` | Cuentas ficticias de demostración |
| `DEMO_PASSWORD` | Contraseña inicial de demostración, mínimo 8 caracteres |
| `PILOT_ONLY` | Si es `true`, solo usuarios autorizados como piloto pueden crear solicitudes |
| `SESSION_DAYS` | Duración de sesiones |
| `APP_ENV` | Identificador del entorno |
| `PUBLIC_BASE_URL` | URL pública declarada |
| `WHATSAPP_ACCESS_TOKEN` | Token Meta Cloud API; dejar vacío para desactivar |
| `WHATSAPP_PHONE_NUMBER_ID` | ID de teléfono de WhatsApp Business |
| `WHATSAPP_GRAPH_VERSION` | Versión de Meta Graph API |
| `WHATSAPP_TEMPLATE_NAME` | Nombre de plantilla aprobada en Meta |

Nunca subir el archivo `.env` ni secretos a GitHub.

## WhatsApp

Para enviar avisos reales de programación: (a) configurar WhatsApp Business Cloud API directamente con Meta, (b) utilizar número habilitado, permisos y token válido, (c) crear una plantilla aprobada con idioma `es` y dos variables de texto: código y fecha/hora, (d) completar las variables del entorno, (e) verificar en `/api/notifications` si Meta aceptó el envío. Sin credenciales, la programación se muestra en la web y se registra **sin_configurar**, sin fingir que se envió un mensaje.

## Pruebas

Con un PostgreSQL de pruebas aislado, crear una base llamada `ecoconecta_test`, definir `TEST_DATABASE_URL` y ejecutar `python -m pytest -q`. El proceso de pruebas reinicia esa **base de pruebas**: jamás utilizar la de producción.

## Limitaciones y publicación

La aplicación no puede considerarse publicada hasta ejecutar el despliegue real y registrar una URL pública con HTTPS. Para hacerlo, sigue `docs/PUBLICACION.md`. No se incluyen llaves ni credenciales ni URL inventada. Los puntos demostrativos no son reglas oficiales de Fundación Santo Domingo.
