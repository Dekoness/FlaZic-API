# Configuración de Gunicorn para Render
bind = "0.0.0.0:${PORT:-10000}"
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120