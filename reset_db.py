# reset_db.py
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def reset_database():
    print("🔄 Reiniciando base de datos...")
    
    try:
        # Importar la base primero
        from app.database import Base, engine
        
        # Importar TODOS los modelos para que SQLAlchemy los registre
        print("📋 Importando modelos...")
        
        # Importar cada modelo individualmente
        from app.models.user import User
        from app.models.track import Track
        from app.models.playlist import Playlist  # ← Agregar este
        from app.models.playlist_track import PlaylistTrack  # ← Agregar este
        from app.models.comment import Comment  # ← Agregar este si existe
        from app.models.like import Like  # ← Agregar este si existe
        from app.models.follower import Follower  # ← Agregar este si existe
        from app.models.social_link import SocialLink  # ← Agregar este si existe
        from app.models.notification import Notification  # ← Agregar este si existe
        from app.models.event import Event  # ← Agregar este si existe
        
        print("✅ Todos los modelos importados")
        
        # Borrar todas las tablas (en orden inverso para evitar FK errors)
        print("🗑️  Eliminando tablas...")
        Base.metadata.drop_all(bind=engine)
        print("✅ Tablas eliminadas")
        
        # Crear todas las tablas con la nueva estructura
        print("🏗️  Creando tablas...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas recreadas con las nuevas columnas")
        
        print("🎉 Base de datos reseteada exitosamente!")
        print("📍 Las nuevas columnas (audio_filename, audio_data, audio_mimetype) han sido agregadas")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que todos los modelos existan en app/models/")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("⚠️  ADVERTENCIA: Esto borrará TODOS los datos de la base de datos")
    confirm = input("¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): ")
    
    if confirm.upper() == 'SI':
        reset_database()
    else:
        print("Operación cancelada")