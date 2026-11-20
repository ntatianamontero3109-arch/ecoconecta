# Subir a GitHub y desplegar en la nube

## Paso 1. Publicar el repositorio

1. Crear una cuenta o ingresar en https://github.com.
2. Crear repositorio nuevo denominado `ecoconecta`, público si así lo exige la evaluación, sin README automático (ya existe).
3. Abrir el proyecto en VS Code y ejecutar desde la terminal:

```bash
git init
git add .
git commit -m "MVP EcoConecta: solicitud, enrutamiento, programación y puntos"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/ecoconecta.git
git push -u origin main
```

4. Enviar a los jurados el enlace real del repositorio, por ejemplo el de tu usuario, y verificar que `README.md` se ve. Los comandos contienen marcadores, no un enlace existente.

## Paso 2. Publicar la aplicación web (no basta GitHub)

GitHub aloja el código; **GitHub Pages no ejecuta FastAPI ni PostgreSQL**. Se necesita además un servidor cloud. La opción de menor complejidad operativa es una VM Ubuntu con Docker Compose (por ejemplo en un proveedor cloud que permita máquinas virtuales y volumen persistente).

1. Crear VM Linux con IP pública, instalar Git, Docker Engine y Docker Compose.
2. Clonar repositorio y crear `.env` en la VM (nunca subirlo a Git). Reemplazar contraseñas de demostración por claves robustas.
3. Ejecutar `docker compose up --build -d` y `docker compose ps`.
4. Validar `curl http://localhost:8000/api/health` y un recorrido completo con cuentas de prueba.
5. Asociar un dominio, configurar un proxy HTTPS (Nginx o equivalente) hacia 127.0.0.1:8000 y emitir certificado TLS. En producción cambiar `ports` del servicio web por `127.0.0.1:8000:8000` para no publicar HTTP directamente.
6. Abrir solo puertos 80 y 443 en firewall externo; no exponer PostgreSQL.
7. Declarar en README del repositorio: URL real https://..., proveedor de VM, CPU/RAM, almacenamiento persistente, red, fecha de despliegue y método de respaldos.
8. Deshabilitar cuentas demo y establecer onboarding seguro y consentimientos antes de recopilar datos personales reales.

## Paso 3. Entrega a jurados

- URL HTTPS real y verificada (plataforma).
- URL GitHub real, con acceso abierto para jurados.
- README: tecnologías, Docker, variables sin valores, credenciales de demostración transmitidas de forma segura.
- `docs/ARQUITECTURA.md` y `docs/ANALISIS_RETO.md`.
- Demo orgánica + reciclable y puntos, según `docs/DEMO_JURADO.md`.

**Nota:** la subida y el despliegue dependen del acceso a una cuenta GitHub y un proveedor de nube; estos pasos no se ejecutan automáticamente desde el paquete entregado.
