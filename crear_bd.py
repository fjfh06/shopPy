from sqlalchemy import create_engine, text
from clases import app, db

# Obtener URI de la configuración
uri = app.config['SQLALCHEMY_DATABASE_URI']
# Extraer el nombre de la base de datos
db_name = uri.split('/')[-1]
# URI base para conectar sin seleccionar base de datos (se asume mysql://user:pass@host:port/dbname)
# Esto es un split simple, podría necesitar más robustez si la URI es compleja
base_uri = uri.rsplit('/', 1)[0]

print(f"Intentando conectar a {base_uri} para crear la BD {db_name}...")

try:
    engine = create_engine(base_uri)
    with engine.connect() as conn:
        # Commit automático necesario para CREATE DATABASE en algunos drivers
        conn.execution_options(isolation_level="AUTOCOMMIT").execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
    print(f"Base de datos '{db_name}' creada o ya existente.")
except Exception as e:
    print(f"Nota: No se pudo crear la base de datos automáticamente (error: {e}). Asegúrate de que exista.")

# Crear tablas
with app.app_context():
    db.create_all()
    print("Tablas creadas exitosamente.")
