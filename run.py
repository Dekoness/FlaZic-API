# import uvicorn
# import os
# from dotenv import load_dotenv

# # Cargar variables de entorno
# load_dotenv()

# if __name__ == "__main__":
#     host = os.getenv("HOST")
#     port = int(os.getenv("PORT"))
    
#     print("🎵 Iniciando FLAZIC-API...")
#     print(f"📍 Servidor: {host}:{port}")
#     print(f"📚 Documentación: http://{host}:{port}/docs")
#     print(f"🔧 Health check: http://{host}:{port}/health")
#     print("🚀 Presiona Ctrl+C para detener el servidor")
    
#     uvicorn.run(
#         "app.main:app",
#         host=host,
#         port=port,
#         reload=True,  # Auto-recarga en desarrollo
#         log_level="info"
#     )


    #--------------DESPLIEGUE-------------#

import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

if __name__ == "__main__":
    # Valores por defecto específicos para Railway
    host = os.getenv("HOST", "0.0.0.0")  # Railway usa 0.0.0.0
    port = int(os.getenv("PORT", 8000))  # Railway asigna PORT automáticamente
    
    print("🎵 Iniciando FLAZIC-API...")
    print(f"📍 Servidor: {host}:{port}")
    print(f"📚 Documentación: http://{host}:{port}/docs")
    print(f"🔧 Health check: http://{host}:{port}/health")
    print("🚀 Presiona Ctrl+C para detener el servidor")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,  # False en producción
        log_level="info"
    )