
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Downloading project from GitHub'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Building Python project'

                script {
                    if (isUnix()) {
                        sh 'python3 -m py_compile server.py'
                    } else {
                        bat 'python -m py_compile server.py'
                    }
                }
            }
        }

        stage('Test') {
            steps {
                echo 'Testing project'
            }
        }
    }

    post {
        success {
            echo 'BUILD SUCCESSFUL'
        }

        failure {
            echo 'BUILD FAILED'
        }
    }
}
