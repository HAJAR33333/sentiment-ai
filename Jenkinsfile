// Jenkinsfile Pipeline CI/CD SentimentAI
pipeline {
    agent any // S'exécute sur n'importe quel agent disponible
    
    environment {
        IMAGE_NAME = 'sentiment-ai'
        REGISTRY = 'ghcr.io/HAJAR33333' // Votre pseudo GitHub complété
        // Capture les 7 premiers caractères du SHA du commit actuel pour un tag unique
        IMAGE_TAG = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
    }
    
    stages {
        // Stage 1 : Récupération du code source
        stage('Checkout') {
            steps {
                checkout scm
                echo "Branche : ${env.BRANCH_NAME}"
                echo "Commit : ${env.GIT_COMMIT}"
                sh 'git log --oneline -5'
            }
        }
        
        // Stage 2 : Analyse de la syntaxe et du style du code (Fail Fast)
        stage('Lint') {
            steps {
                sh '''
                docker run --rm \
                    --volumes-from jenkins \
                    -w $WORKSPACE \
                    python:3.12-slim \
                    sh -c "pip install flake8 -q && flake8 src/ --max-line-length=100"
                '''
            }
        }
        
        // Stage 3 : Construction de l'image et exécution des tests avec génération de coverage.xml
        stage('Build & Test') {
            steps {
                sh '''
                docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                
                # Supprimer un éventuel conteneur test-runner résiduel
                docker rm -f test-runner 2>/dev/null || true
                
                # Désactiver temporairement l'arrêt strict de bash
                set +e
                
                # Lancer les tests en forçant le chemin relatif dans le rapport de couverture
                docker run \
                  -e CI=true \
                  --name test-runner \
                  ${IMAGE_NAME}:${IMAGE_TAG} \
                  pytest tests/ -v \
                  --cov=src \
                  --cov-report=xml:coverage.xml \
                  --cov-report=term-missing \
                  --cov-fail-under=70
                
                TEST_EXIT_CODE=$?
                set -e
                
                # Copier le rapport de couverture depuis le dossier de l'app du conteneur vers le workspace local
                docker cp test-runner:/app/coverage.xml ./coverage.xml 2>/dev/null || true
                
                # Nettoyer le conteneur de test
                docker rm -f test-runner 2>/dev/null || true
                
                # Retourner le code de sortie des tests
                exit $TEST_EXIT_CODE
                '''
            }
            post {
                failure {
                    echo 'Tests échoués ou couverture de code insuffisante (< 70%).'
                }
            }
        }

        // Stage 4 : Analyse Statique du Code Source via SonarQube
        stage('SonarQube Analysis') {
            environment {
                SONARQUBE_TOKEN = credentials('sonar-token')
            }
            steps {
                withSonarQubeEnv('sonarqube') {
                    sh '''
                    docker run --rm \
                      --network cicd-network \
                      --volumes-from jenkins \
                      -w "$WORKSPACE" \
                      -e SONAR_HOST_URL="$SONAR_HOST_URL" \
                      -e SONAR_TOKEN="$SONARQUBE_TOKEN" \
                      sonarsource/sonar-scanner-cli:latest \
                      sonar-scanner \
                      -Dsonar.projectKey=SentimentAI \
                      -Dsonar.projectName=SentimentAI \
                      -Dsonar.projectBaseDir="$WORKSPACE" \
                      -Dsonar.sources=src \
                      -Dsonar.python.version=3.11 \
                      -Dsonar.python.coverage.reportPaths=coverage.xml \
                      -Dsonar.sourceEncoding=UTF-8 \
                      -Dsonar.scanner.metadataFilePath=$WORKSPACE/report-task.txt
                    '''
                }
            }
        }

        // Stage 5 : Attente du verdict du Quality Gate (bloquant)
        stage('Quality Gate') {
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    // Attend le résultat asynchrone du Quality Gate SonarQube
                    // abortPipeline: true => bloque Push et Deploy si le gate échoue
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        // Stage 6 : Scan de vulnérabilités de l'image de l'application via Trivy
        stage('Security Scan') {
            steps {
                sh '''
                # --exit-code 0 pour afficher le rapport de CVE sans bloquer ni faire échouer le pipeline
                # --format table pour avoir un rapport lisible directement dans les logs Jenkins
                docker run --rm \
                  -v /var/run/docker.sock:/var/run/docker.sock \
                  -v trivy-cache:/root/.cache/trivy \
                  aquasec/trivy:latest image \
                  --severity HIGH,CRITICAL \
                  --exit-code 0 \
                  --format table \
                  "${IMAGE_NAME}:${IMAGE_TAG}"
                '''
            }
            post {
                failure {
                    echo 'Vulnérabilités CRITICAL ou HIGH détectées !'
                    echo 'Corrigez les dépendances avant de déployer.'
                }
            }
        }
        
        // Stage 7 : Publication de l'image sur GitHub Packages (uniquement sur main)
        stage('Push') {
            when { branch 'main' }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-token',
                    usernameVariable: 'REGISTRY_USER',
                    passwordVariable: 'REGISTRY_PASS'
                )]) {
                    sh """
                    echo \$REGISTRY_PASS | docker login ghcr.io -u \$REGISTRY_USER --password-stdin
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:latest
                    docker push ${REGISTRY}/${IMAGE_NAME}:latest
                    """
                }
            }
        }

        // Stage 8 : Déploiement simulé en Staging via docker-compose
        stage('Deploy Staging') {
            when { branch 'main' }
            steps {
                echo "Déploiement de ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} en staging..."
                sh '''
                # Arrêter le staging précédent proprement
                docker compose -f docker-compose.yml -p staging down 2>/dev/null || true
                # Démarrer la nouvelle version
                docker compose -f docker-compose.yml -p staging up -d
                echo "Staging disponible sur http://localhost:8001"
                '''
            }
        }
    }
    
    post {
        always {
            // Nettoyage des conteneurs après l'exécution
            sh 'docker compose down -v 2>/dev/null || true'
        }
        success {
            echo "Pipeline réussi ! Image publiée : ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo 'Pipeline échoué. Consultez les logs ci-dessus.'
        }
    }
}