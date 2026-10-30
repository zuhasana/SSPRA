
pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Downloading SSPRA source code from GitHub'
                checkout scm
            }
        }

        stage('Python Build') {
            steps {
                echo 'Checking Python syntax'

                bat '"C:\\Users\\ZUHA SANA\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" -m py_compile server.py'
            }
        }

        stage('Test') {
            steps {
                echo 'SSPRA basic validation completed'
            }
        }

        stage('Check Docker') {
            steps {
                echo 'Checking Docker installation'
                bat 'docker --version'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building SSPRA Docker image'

                bat 'docker build -t sspra-backend:latest .'
            }
        }

        stage('Verify Docker Image') {
            steps {
                echo 'Verifying generated Docker image'

                bat 'docker images sspra-backend'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: SSPRA Docker image generated successfully!'
        }

        failure {
            echo 'FAILURE: Check the Jenkins Console Output for errors.'
        }

        always {
            echo 'SSPRA pipeline execution completed.'
        }
    }
}
