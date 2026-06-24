# Définition des variables
IMAGE_NAME=sentiment-ai
TAG=latest
PORT_HOST=8081
PORT_CONTAINER=8000

.PHONY: build run test clean

# 1. Étape de Build de l'image Docker (sans cache pour éviter les anciens bugs)
build:
	docker build --no-cache -t $(IMAGE_NAME):$(TAG) .

# 2. Étape de lancement du conteneur autonome
run:
	docker run -d --name sentiment -p $(PORT_HOST):$(PORT_CONTAINER) $(IMAGE_NAME):$(TAG)

# 3. Étape d'exécution des tests unitaires avec calcul de la couverture (Coverage)
test:
	pytest --cov=src tests/

# 4. Étape de nettoyage des conteneurs et fichiers temporaires
clean:
	docker rm -f sentiment || true
	docker compose down || true
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 5. Étape de taggage automatique de la version
tag:
	git tag -a v0.1.0 -m "Initial SentimentAI release"
	git push origin v0.1.0	