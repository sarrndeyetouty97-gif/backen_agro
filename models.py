from sqlalchemy import Column, Float, Integer, String

from database import Base

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class Client(Base):
    """
    Modèle SQLAlchemy pour la table des clients.
    """
    __tablename__ = "clients"

    id_client = Column(Integer, primary_key=True, index=True,autoincrement=True)
    full_name = Column(String(255), index=True,nullable=False)
    email = Column(String(255), unique=True, index=True)
    telephone = Column(String(20), unique=True, index=True,nullable=False)


class Produit(Base):
    """
    Modèle SQLAlchemy pour la table des produits.
    """
    __tablename__ = "produits"

    id_produit = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True,nullable=False)
    prix = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False,default=0)


class Commande(Base):
    __tablename__ = "commandes"

    id_commande = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id_client")) # Relie au client
    produit_id = Column(Integer, ForeignKey("produits.id_produit")) # Relie au produit
    quantite = Column(Integer, nullable=False)
    total_prix = Column(Float)
    date_commande = Column(String(100), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Relations pour faciliter la lecture des données plus tard
    client = relationship("Client")
    produit = relationship("Produit")