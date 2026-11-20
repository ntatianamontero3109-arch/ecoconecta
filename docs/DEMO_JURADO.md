# Guion de demostración para jurados (5–7 minutos)

**Preparación:** ejecutar `docker compose up --build` y abrir `http://localhost:8000`. Acceder con la contraseña definida en `.env` para las cuentas ficticias, nunca con datos personales reales.

1. **Problema y solución:** mostrar portada, sección de educación y dos rutas diferenciadas.
2. **Unidad productiva:** ingresar con `comercio@ecoconecta.demo`; registrar solicitud orgánica indicando dirección ficticia, teléfono y preferencia horaria. Anotar código ECO.
3. **Coordinación huerta:** ingresar con `coordinador.huerta@ecoconecta.demo`; ver la solicitud en su bandeja; marcar en revisión y asignar a `huertero@ecoconecta.demo`.
4. **Programación:** registrar fecha futura acordada. Regresar a la cuenta de comercio y mostrar la fecha/hora y el nombre del responsable.
5. **Huertero:** ingresar con `huertero@ecoconecta.demo`; abrir la solicitud y completar con 3,5 kg. Demostrar 35 puntos con regla piloto de 10 puntos/kg y cierre trazable.
6. **Segundo flujo:** con `vecina@ecoconecta.demo` solicitar reciclables. En `coordinador.reciclaje@ecoconecta.demo` verificar que llega solamente a su bandeja y asignar a `reciclador@ecoconecta.demo`.
7. **Seguridad:** desde coordinación reciclaje, intentar abrir una solicitud orgánica mediante API (`/api/docs`): recibe 403. Repetir el cierre: recibe 409.
8. **Administración:** `admin@ecoconecta.demo` permite revisar usuarios piloto, consultar reglas y publicar guías. Mostrar notificaciones con estado real si se ha conectado Meta.

**Mensaje clave:** La plataforma no solo crea una solicitud; demuestra el circuito completo verificable y dos colectivos independientes.

**No afirmar sin verificación:** que WhatsApp fue enviado, que la aplicación está en nube, que las tasas de puntos son oficiales o que existen métricas de impacto reales.
