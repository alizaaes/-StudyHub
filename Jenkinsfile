
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

        stage('Build Docker image') {
            steps {
                sh 'docker build -t studyhub:latest .'
            }
        }
    }
}
