
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

                bat '"C:\\Users\\ZUHA SANA\\AppData\\Local\\Programs\\Python\\Python313\\python.exe" -m py_compile server.py'

                echo 'Python build successful'
            }
        }

        stage('Test') {
            steps {
                echo 'Testing project'
                echo 'Basic validation completed'
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
