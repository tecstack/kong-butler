pipeline {
  agent none
  stages {
    stage('env init') {
      steps {
        sh 'docker run -it -d --name=promise-bulker --hostname=promise-bulker-dev-ci -v /etc/localtime:/etc/localtime:ro -e "PYTHONPATH=/apps/svr/promise-back" promise-base /usr/sbin/init'
        sh '''docker exec promise-bulker-dev-ci git clone http://192.168.182.51/promise/promise-bulker.git /apps/svr/promise-bulker
docker exec promise-bulker-dev-ci cp /apps/svr/promise-bulker/env.conf/my.cnf /etc/
docker exec promise-bulker-dev-ci chmod 0644 /etc/my.cnf
# docker cp /apps/data/tomcat_8080/jenkins_file/promise-back/promise-bulker-dev-ci/dev-ci-instance promise-bulker-dev-ci:/apps/svr/promise-bulker/
docker exec promise-bulker-dev-ci pip install -r /apps/svr/promise-bulker/requirements.txt'''
      }
    }
  }
}