from fastapi . testclient import TestClient
from src . main import app
client = TestClient ( app )
def test_health () :
"""Vé rifie que l’endpoint / health ré pond avec status 200. """
r = client . get ("/ health ")
assert r . status_code == 200
def test_predict_positive () :
"""Vé rifie qu ’une pré diction retourne la bonne structure de ré ponse .""
"
r = client . post ("/ predict ", json ={" text ": "Ce produit est excellent !"
})
assert r . status_code == 200
data = r . json ()
# Le label doit être l’une des 3 valeurs attendues
assert data [" label "] in [" POSITIVE ", " NEGATIVE ", " NEUTRAL "]
# Le score doit être un nombre entre 0 et 1
assert 0 <= data [" score "] <= 1
def test_predict_empty_fails () :
"""Vé rifie que Pydantic rejette un texte vide avec une erreur 422. """
r = client . post ("/ predict ", js