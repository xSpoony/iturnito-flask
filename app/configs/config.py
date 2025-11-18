import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Esta es la ruta de respaldo (fallback)
DEFAULT_DB_PATH = os.path.join(BASE_DIR, 'instance', 'database.sqlite')

class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY')

    # 1. Intenta leer 'DATABASE_URL' desde el .env 
    # 2. Si no la encuentra, usa la ruta por defecto a 'instance/database.sqlite'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{DEFAULT_DB_PATH}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
 