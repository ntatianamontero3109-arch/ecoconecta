# Instalación de EcoConecta en Windows 11

## Programas necesarios

1. **Docker Desktop para Windows**: https://www.docker.com/products/docker-desktop/
   - Durante la instalación, utilizar el backend WSL 2 si el instalador lo ofrece.
   - Si solicita WSL, abrir PowerShell como administrador y ejecutar `wsl --install`; reiniciar Windows y abrir Docker Desktop.
   - Esperar a que Docker indique que está en ejecución.
2. **Visual Studio Code**: https://code.visualstudio.com/ (editor recomendado).
3. **Git para Windows**: https://git-scm.com/download/win (necesario para publicar el repositorio en GitHub).

## No necesitas instalar por separado para arrancar con Docker

- PostgreSQL: Docker descargará y ejecutará PostgreSQL 16 en un contenedor.
- Python: el backend se instala dentro de la imagen Docker.
- Node.js: este proyecto usa HTML, CSS y JavaScript sin proceso de compilación Node.

## Arranque local

1. Descomprime `EcoConecta_Proyecto.zip` en una carpeta fácil de encontrar, por ejemplo `Documentos`.
2. Abre VS Code y selecciona **Archivo > Abrir carpeta**. Elige la carpeta `ecoconecta` (la que contiene `docker-compose.yml`).
3. En el explorador de VS Code, copia `.env.example` y pega el duplicado con el nombre `.env`.
4. Abre **Terminal > Nueva terminal**. Comprueba que la terminal está ubicada en la carpeta que contiene `docker-compose.yml`.
5. Ejecuta:

```powershell
docker compose up --build -d
```

6. La primera ejecución descarga imágenes y puede tardar varios minutos. Luego abre:
   - Aplicación: http://localhost:8000
   - Documentación de API: http://localhost:8000/api/docs
   - Estado del servicio: http://localhost:8000/api/health

## Comandos útiles

```powershell
# Ver los contenedores
docker compose ps

# Ver los registros si algo falla
docker compose logs -f

# Detener la aplicación sin borrar la base de datos
docker compose down

# Detener y borrar también los datos locales de PostgreSQL (acción destructiva)
docker compose down -v
```

## Cuentas de demostración

La contraseña para todas las cuentas es el valor de `DEMO_PASSWORD` en `.env` (en el ejemplo inicial: `EcoConecta2026!`).

- Comunidad: `vecina@ecoconecta.demo`
- Unidad productiva: `comercio@ecoconecta.demo`
- Coordinador de huerteros: `coordinador.huerta@ecoconecta.demo`
- Coordinador de recicladores: `coordinador.reciclaje@ecoconecta.demo`
- Huertero: `huertero@ecoconecta.demo`
- Reciclador: `reciclador@ecoconecta.demo`
- Administrador: `admin@ecoconecta.demo`

Son usuarios ficticios para pruebas. Cambia la contraseña y desactiva la siembra de demostración antes de cualquier despliegue público. No subas `.env` a GitHub.

## Si Docker no inicia

- Reinicia el equipo después de instalar WSL 2.
- Abre Docker Desktop y espera a que termine de iniciar.
- En PowerShell ejecuta `wsl --status` y `docker compose version`.
- Si el puerto 8000 está ocupado, cierra la aplicación que lo usa antes de iniciar EcoConecta.

## Publicación

El ZIP permite ejecutar el proyecto localmente. Para tener un enlace público todavía hay que crear el repositorio GitHub y desplegar backend y PostgreSQL en una infraestructura compatible. No se debe presentar `localhost` como enlace público. Sigue `PUBLICACION.md` y configura secretos seguros en el proveedor de nube.
