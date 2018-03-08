pipeline {
  agent {
    docker {
      image '192.168.182.52:5000/promise-base:v1.0'
    }
    
  }
  stages {
    stage('env init') {
      steps {
        sh '''git clone http://192.168.182.51/promise/promise-bulter.git /apps/svr/promise-bulter
cp /apps/svr/promise-bulker/env.conf/my.cnf /etc/
chmod 0644 /etc/my.cnf
pip install -r /apps/svr/promise-bulker/requirements.txt'''
      }
    }
  }
  environment {
    PYTHONPATH = '/apps/svr/promise-bulter'
  }
}