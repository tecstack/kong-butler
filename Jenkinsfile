pipeline {
  agent {
    docker {
      image '192.168.182.52:5000/promise-base'
    }
    
  }
  stages {
    stage('code download') {
      steps {
        git(changelog: true, url: 'git@192.168.182. 51:promise/promise-bulter.git', branch: 'dev', poll: true, credentialsId: 'FNvGHXQu3t2Wik3fgcXL')
        waitUntil()
      }
    }
  }
  environment {
    PYTHONPATH = '/apps/svr/promise-bulter'
  }
}