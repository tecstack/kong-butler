pipeline {
  agent {
    node {
      label 'master'
    }
    
  }
  stages {
    stage('docker init') {
      steps {
        sh '''if [ -n "`docker ps -a |grep promise-bulter-dev-ci`" ]; then (docker stop promise-bulter-dev-ci)&&(docker rm promise-bulter-dev-ci); fi
docker run -it -d --name=promise-bulter-dev-ci --hostname=promise-bulter-dev-ci -v /etc/localtime:/etc/localtime:ro -e "PYTHONPATH=/apps/svr/promise-bulter" promise-base:v1.0 /usr/sbin/init'''
      }
    }
    stage('file download') {
      steps {
        sh '''docker exec promise-bulter-dev-ci git clone http://192.168.182.51/promise/promise-bulter.git /apps/svr/promise-bulter
docker exec promise-bulter-dev-ci cp /apps/svr/promise-bulter/env.conf/my.cnf /etc/
docker exec promise-bulter-dev-ci chmod 0644 /etc/my.cnf
docker exec promise-bulter-dev-ci cp -r /apps/svr/promise-bulter/env.conf/dev-ci-instance /apps/svr/promise-bulter/instance
'''
      }
    }
    stage('lib install') {
      steps {
        sh 'docker exec promise-bulter-dev-ci pip install -r /apps/svr/promise-bulter/requirements.txt'
      }
    }
    stage('code check') {
      steps {
        sh '''docker exec promise-bulter-dev-ci flake8 /apps/svr/promise-bulter/bulter --config=/apps/svr/promise-bulter/tox.ini
'''
      }
    }
    stage('nosetests') {
      steps {
        sh '''docker exec promise-bulter-dev-ci nosetests -c /apps/svr/promise-bulter/nosetests.ini
docker cp promise-bulter-dev-ci:/apps/svr/promise-bulter/nosetests.xml /apps/data/jenkins/test-results/promise-bulter-dev-ci/
docker cp promise-bulter-dev-ci:/apps/svr/promise-bulter/coverage.xml /apps/data/jenkins/test-results/promise-bulter-dev-ci/'''
      }
    }
  }
  post {
    always {
        junit '/apps/data/jenkins/test-results/promise-bulter-dev-ci/nosetests.xml'
        step([$class: 'CoberturaPublisher', autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: '/apps/data/jenkins/test-results/promise-bulter-dev-ci/coverage.xml', failUnhealthy: false, failUnstable: false, maxNumberOfBuilds: 0, onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])
    }
  }
}