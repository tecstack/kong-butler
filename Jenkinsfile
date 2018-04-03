pipeline {
  agent {
    node {
      label 'master'
      customWorkspace '/apps/data/jenkins/workspace/promise-butler-dev-ci'
    }
    
  }
  stages {
    stage('docker init') {
      steps {
        sh '''if [ -n "`docker ps -a |grep promise-butler-dev-ci`" ]; then (docker stop promise-butler-dev-ci)&&(docker rm promise-butler-dev-ci); fi
docker run -it -d --name=promise-butler-dev-ci --hostname=promise-butler-dev-ci -v /etc/localtime:/etc/localtime:ro -e "PYTHONPATH=/apps/svr/promise-butler" promise-base:v1.0 /usr/sbin/init'''
      }
    }
    stage('file download') {
      steps {
        sh '''docker exec promise-butler-dev-ci git clone http://192.168.182.51/promise/promise-butler.git /apps/svr/promise-butler
docker exec promise-butler-dev-ci cp /apps/svr/promise-butler/env.conf/my.cnf /etc/
docker exec promise-butler-dev-ci chmod 0644 /etc/my.cnf
docker exec promise-butler-dev-ci cp -r /apps/svr/promise-butler/env.conf/dev-ci-instance /apps/svr/promise-butler/instance
'''
      }
    }
    stage('lib install') {
      steps {
        sh 'docker exec promise-butler-dev-ci pip install -r /apps/svr/promise-butler/requirements.txt'
      }
    }
    stage('code check') {
      steps {
        sh '''docker exec promise-butler-dev-ci flake8 /apps/svr/promise-butler/butler --config=/apps/svr/promise-butler/tox.ini
'''
      }
    }
    stage('nosetests') {
      steps {
        sh '''docker exec promise-butler-dev-ci nosetests -c /apps/svr/promise-butler/nosetests.ini
docker cp promise-butler-dev-ci:/apps/svr/promise-butler/nosetests.xml $WORKSPACE
docker cp promise-butler-dev-ci:/apps/svr/promise-butler/coverage.xml $WORKSPACE'''
      }
    }
  }
  post {
    always {
      junit '**/nosetests.xml'
      step([$class: 'CoberturaPublisher', autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: '**/coverage.xml', failUnhealthy: false, failUnstable: false, maxNumberOfBuilds: 0, onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])
    }
    success{
      sh '''(docker stop promise-butler-dev-ci)&&(docker rm promise-butler-dev-ci)'''
    }
  }
}