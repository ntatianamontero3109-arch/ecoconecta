# Análisis de requisitos y criterios de aceptación

Fuente: *Reto Oficial Hackathon EcoConecta – Villas de San Pablo*, 7 páginas, Universidad Libre y Fundación Santo Domingo (noviembre de 2026).

## Problema y usuarios

Existe comunicación fragmentada entre hogares, unidades productivas, huerteros y recicladores. El proyecto reemplaza el registro informal por un canal accesible, pero no sustituye la coordinación humana. Perfiles contemplados: comunidad/hogar, unidad productiva, coordinador huerteros, huertero, coordinador recicladores, reciclador y administrador.

## Matriz de trazabilidad

| Criterio | Implementación | Cómo demostrar |
|---|---|---|
| RN-01, separación de flujos | Campo `waste_type`, bandejas y control de rol | Solicitar orgánicos y reciclables; cada coordinación ve solo lo suyo |
| RN-02, programación completa | Endpoint `schedule` exige coordinador, recolector y fecha futura | Intentar programar antes de asignar y verificar rechazo; luego programar |
| RN-03, asignación | IDs de coordinador y recolector, validación de colectivo | Asignar huertero a orgánicos y reciclador a reciclables |
| RN-04, trazabilidad | Código `ECO-...`, estado e historial `request_events` | Consultar detalle e historial |
| RN-05, cierre antes de puntos | `complete` requiere `programada`, `point_entries` único por solicitud | Ver 0 puntos antes, suma al cerrar, rechazar segundo cierre |
| RN-06, puntos explicables | `point_rules`: puntos/kg y fórmula guardada | Cambiar regla desde admin y registrar peso |
| RN-07, privacidad | RBAC de acceso a endpoints; contacto no visible fuera del equipo involucrado | Acceso denegado a otro colectivo |
| RN-08, piloto | Bandera `is_pilot` y `PILOT_ONLY` | Admin activa participantes; probar con bandera estricta |
| Información ambiental | Artículos de separación, rutas y huerta | Landing y sección Educación |
| Historial y panel | Estadísticas por flujo/estado/peso y panel por perfil | Ver Resumen y Solicitudes |
| WhatsApp Business Cloud API | Integración de plantilla; registro de resultado | Configurar acceso real y aprobar plantilla de Meta; sin credenciales, registro `sin_configurar` |
| Docker + Git + PostgreSQL | Dockerfile, Compose, archivos separados | `docker compose up --build` |
| Despliegue público | Código preparado para VM; URL requiere infraestructura propia | Abrir URL una vez desplegado |

## Estados de solicitud

`recibida → en_revision → asignada → programada → recolectada`

Alternativa: `cancelada` antes del cierre. El historial no se borra y cada transición queda registrada.

## Puntos de ejemplo

Regla demostrativa: **10 puntos por kilogramo**, tanto para orgánicos como reciclables. Fórmula: `floor(kg × puntos_por_kg)`. Esta configuración es **provisional y no está validada por FSD**; jamás presentarla como oficial. Solo el administrador puede cambiarla.

## Accesibilidad y experiencia

Diseño responsive, navegación sencilla, formularios breves, estados con texto, contraste visual, mensajes de error en español. Mejoras antes de producción: pruebas asistidas de accesibilidad WCAG 2.2, simplificación del ingreso, validación con huerteros y comunidad, textos en lenguaje claro revisados territorialmente.

## Alcance real y limitaciones

**Implementado:** frontend, API, autenticación, roles, artículos, solicitudes, enrutamiento, asignación, programación, cierre, puntos, trazabilidad, panel y configuración piloto.

**Preparado pero dependiente de terceros:** envío WhatsApp real (Meta Cloud API, número e integración, plantilla aprobada); despliegue en un proveedor cloud y URL pública.

**No implementado:** asistente de IA; no es obligatorio según el reto y se priorizó el recorrido central. No existen horarios oficiales ni equivalencias de puntos validadas; no se inventaron.

## Indicadores de impacto propuestos

Número de solicitudes por flujo, porcentaje recolectado, kg registrados, puntos otorgados y tiempos entre solicitud/programación/cierre. Los datos iniciales son demostrativos; cualquier estimación de reducción de residuos requeriría medición territorial real.
