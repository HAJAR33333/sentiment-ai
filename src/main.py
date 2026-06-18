from fastapi import FastAPI
from src . schemas import PredictionRequest , PredictionResponse
from src . model import SentimentModel
app = FastAPI ( title =" SentimentAI ", version =" 0.1.0 ")
# Le modèle est charg é une seule fois au dé marrage du serveur
model = SentimentModel ()
@app . get ("/ health ")
def health () :
""" Endpoint de healthcheck utilis é par Docker et les load balancers .""
"
return {" status ": "ok"}
@app . post ("/ predict ", response_model = PredictionResponse )
def predict ( request : PredictionRequest ) :
""" Analyse le sentiment du texte fourni 