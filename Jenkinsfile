
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Syntax check') {
            steps {
                sh '.venv/bin/python -m compileall -q app.py database.py'
            }
        }

        stage('Automated tests') {
            steps {
                sh '.venv/bin/python -m pytest -v'
            }
        }

        stage('Build Docker image') {
            steps {
                sh 'docker build -t studyhub:latest .'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f studyhub-app || true

                    docker run -d \
                        --name studyhub-app \
                        --network studyhub_complete_starter_default \
                        --network-alias studyhub \
                        --restart unless-stopped \
                        -e SECRET_KEY="replace-with-a-long-random-secret" \
                        -e DATA_DIR="/app/data" \
                        -v studyhub_complete_starter_studyhub_data:/app/data \
                        studyhub:latest
                '''
            }
        }
    }
}
