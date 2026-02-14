from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import database
import uvicorn


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Création des tables dans la base de données si elles n'existent pas
models.Base.metadata.create_all(bind=database.engine)

@app.get("/", response_class=HTMLResponse)
def read_item(request: Request, db: Session = Depends(database.get_db)):
    produits = db.query(models.Produit).all()
    return templates.TemplateResponse("index.html", {"request": request, "produits": produits})



@app.post("/clients/")
def create_client(full_name: str, email: str, telephone: str, db: Session = Depends(database.get_db)):
    nuevo_client = models.Client(full_name=full_name, email=email, telephone=telephone)
    db.add(nuevo_client)
    db.commit()
    db.refresh(nuevo_client)
    return {"status": "Client enregistré !", "id": nuevo_client.id_client}

    # Route pour ajouter un produit (Jus de Bissap, Bouye, etc.)
@app.post("/produits/")
def create_product(name: str, prix: float, stock: int, db: Session = Depends(database.get_db)):
    nuevo_prod = models.Produit(name=name, prix=prix, stock_quantity=stock)
    db.add(nuevo_prod)
    db.commit()
    db.refresh(nuevo_prod)
    return {"message": "Produit ajouté !", "nom": nuevo_prod.name}

# Route pour voir tout ton catalogue en un clic
@app.get("/produits/")
def list_products(db: Session = Depends(database.get_db)):
    return db.query(models.Produit).all()

@app.post("/commander/")
def passer_commande(client_id: int, produit_id: int, quantite: int, db: Session = Depends(database.get_db)):
    # 1. Vérifier si le produit existe et s'il y a assez de stock
    produit = db.query(models.Produit).filter(models.Produit.id_produit == produit_id).first()
    if not produit or produit.stock_quantity < quantite:
        return {"erreur": "Stock insuffisant ou produit inexistant"}

    # 2. Calculer le prix total
    total = produit.prix * quantite

    # 3. Créer la commande
    nouvelle_commande = models.Commande(
        client_id=client_id, 
        produit_id=produit_id, 
        quantite=quantite, 
        total_prix=total
    )
    
    # 4. Mettre à jour le stock
    produit.stock_quantity -= quantite

    db.add(nouvelle_commande)
    db.commit()
    db.refresh(nouvelle_commande)
    
    return {
        "message": "Commande réussie !", 
        "total_a_payer": total,
        "nouveau_stock": produit.stock_quantity
    }

@app.get("/statistiques/chiffre-affaires")
def calculer_ca(db: Session = Depends(database.get_db)):
    # On demande à la base de données de calculer la somme de la colonne total_prix
    total = db.query(func.sum(models.Commande.total_prix)).scalar()
    
    # On compte aussi le nombre total de commandes passées
    nombre_commandes = db.query(models.Commande).count()
    
    return {
        "chiffre_affaires_total": total if total else 0,
        "nombre_de_ventes": nombre_commandes,
        "devise": "FCFA"
    }


@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/facture/{commande_id}")
def generer_facture(commande_id: int, db: Session = Depends(database.get_db)):
    # Récupérer la commande avec les infos du client et du produit
    commande = db.query(models.Commande).filter(models.Commande.id_commande == commande_id).first()
    
    if not commande:
        return {"erreur": "Facture introuvable"}

    return {
        "ENTREPRISE": "SUNU TRANSFORMATION AGRO",
        "NUMERO_FACTURE": f"FAC-{commande.id_commande}",
        "DATE": commande.date_commande,
        "CLIENT": commande.client.nom,  # On récupère le nom via la relation
        "DETAILS": {
            "PRODUIT": commande.produit.name,
            "QUANTITE": commande.quantite,
            "PRIX_UNITAIRE": commande.produit.prix,
            "TOTAL_A_PAYER": f"{commande.total_prix} FCFA"
        },
        "MESSAGE": "Merci de votre confiance !"
    }

@app.get("/facture-pro/{commande_id}", response_class=HTMLResponse)
def voir_facture_pro(request: Request, commande_id: int, db: Session = Depends(database.get_db)):
    commande = db.query(models.Commande).filter(models.Commande.id_commande == commande_id).first()
    
    if not commande:
        return {"erreur": "Commande introuvable"}

    return templates.TemplateResponse("facture.html", {
        "request": request,
        "id": commande.id_commande,
        "date": commande.date_commande,
        "client_nom": commande.client.nom,
        "produit_nom": commande.produit.name,
        "quantite": commande.quantite,
        "total": commande.total_prix
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)