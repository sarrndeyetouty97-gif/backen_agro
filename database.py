from  sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# L'URL de ta base MySQL (XAMPP/WAMP par défaut)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/sunu_transformation"

# Création du moteur
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Création d'une session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour nos modèles
Base = declarative_base()

# Fonction pour obtenir la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()