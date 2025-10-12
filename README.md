((EN DESARROLLO))

🎵 Flazic API - Backend para Plataforma Musical
Backend API para una aplicación web de música destinada a oyentes y artistas emergentes. Desarrollado con FastAPI y SQLAlchemy.

🚀 Características
✅ Módulos Implementados
🔐 Autenticación JWT - Registro, login y gestión de usuarios

👤 Perfiles de Usuario - Sistema completo de perfiles para oyentes y artistas

🎵 Gestión de Tracks - Subir, editar, eliminar y reproducir música

💬 Sistema de Comentarios - Comentarios y respuestas en tracks

❤️ Sistema de Likes - Interacción social con la música

🛠️ Tecnologías
Framework: FastAPI

Base de Datos: SQLite (Desarrollo) + SQLAlchemy ORM

Autenticación: JWT + Argon2

Documentación: Auto-generada en /docs

Python: 3.8+

📦 Instalación
1. Clonar el repositorio
bash
git clone https://github.com/tuusuario/flazic-api.git
cd flazic-api
2. Configurar entorno virtual
bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
3. Instalar dependencias
bash
pip install -r requirements.txt
4. Configurar variables de entorno
Crear archivo .env:

env
# Base de Datos
DATABASE_URL=sqlite:///./flazic.db

# Seguridad JWT
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Argon2
ARGON2_SALT=tu_salt_seguro_para_argon2
5. Ejecutar la aplicación
bash
uvicorn app.main:app --reload || python run.py
La API estará disponible en: http://localhost:3000

📚 Documentación API
Una vez ejecutada la aplicación, accede a:

📖 Documentación Interactiva: http://localhost:3000/docs

📄 Documentación Alternativa: http://localhost:3000/redoc

🎯 Endpoints Principales

🔐 Autenticación

http

POST /auth/register     # Registrar nuevo usuario

POST /auth/login        # Iniciar sesión

GET  /auth/me          # Perfil del usuario actual

👤 Usuarios

http

GET  /users/           # Listar usuarios

GET  /users/{id}       # Obtener usuario específico

PUT  /users/profile    # Actualizar perfil propio

GET  /users/{id}/tracks # Tracks del usuario

🎵 Tracks Musicales

http

GET    /tracks/          # Listar tracks públicos

POST   /tracks/          # Crear nuevo track (Artistas)

PUT    /tracks/{id}      # Actualizar track

DELETE /tracks/{id}      # Eliminar track

POST   /tracks/{id}/like # Dar/quitar like

GET    /tracks/{id}/like # Mostrar cantidad like

💬 Comentarios

http

POST /comments/              # Crear comentario

GET  /comments/{id}          # Obtener comentario

PUT  /comments/{id}          # Actualizar comentario

DELETE /comments/{id}        # Eliminar comentario

POST  /comments/             # Crear respuesta comentario

GET  /comments/{id}/replies  # Listar respuesta comentario



👥 Roles de Usuario
🎧 Oyente
Escuchar música

Comentar tracks

Dar likes

Seguir artistas

🎤 Artista Emergente
Subir tracks

Gestionar su música

Ver estadísticas

Conectar con fans

🚧 Próximas Características
🔄 Sistema de Seguidores

📊 Playlists personalizadas

🎚️ Subida de archivos de audio

📈 Analytics para artistas

🔔 Sistema de notificaciones

🌐 Integración con redes sociales

👨‍💻 Desarrollo
Creado con ❤️ para la comunidad musical emergente.

⭐ ¡Dale una estrella al proyecto si te gusta!
