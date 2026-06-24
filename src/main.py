from fastapi import FastAPI
from src.schemas import PredictionRequest, PredictionResponse
from src.model import SentimentModel

app = FastAPI(title="SentimentAI", version="0.1.0")

# Le modèle est chargé une seule fois au démarrage du serveur
model = SentimentModel()

@app.get("/health")
def health():
    """Endpoint de healthcheck utilisé par Docker et les load balancers."""
    return {"status": "ok"}

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """Analyse le sentiment du texte fourni."""
    # Assurez-vous que le reste de votre logique de prédiction est bien indenté ici
    # Exemple (à adapter selon votre code original) :
    prediction = model.predict(request.text)
    return prediction






    