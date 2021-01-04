import optparse
import sys 

def main(appname):
    print("\nCreating configs for %s\n" % appname) 
    
    fc = open('.gitlab-ci.yml', 'w')
    fc.write(gitlab_c.replace('{{appname}}', appname))
    fc.flush()
    fc.close()

    fc = open('rancher-compose.yml', 'w')
    fc.write(rancher_c.replace('{{appname}}', appname))
    fc.flush()
    fc.close()

    fc = open('docker-compose.yml', 'w')
    fc.write(docker_c.replace('{{appname}}', appname))
    fc.flush()
    fc.close()


gitlab_c = """
before_script:
  - curl -LO https://releases.rancher.com/cli/v0.6.2/rancher-linux-amd64-v0.6.2.tar.gz
  - tar zxf rancher-linux-amd64-v0.6.2.tar.gz
  
build_test:
  script:
    - docker build -t dockerimages.fhcrc.org/{{appname}}:latest .
    - |
        if docker ps -a|tr -s ' '|rev|cut -d ' ' -f 1|rev|grep -q {{appname}}
        then
        docker stop {{appname}} && docker rm --force {{appname}}
        fi
    - docker run -d --name {{appname}} -p 3838:3838 dockerimages.fhcrc.org/{{appname}}:latest
    - sleep 15 && curl -sI  http://localhost:3838  |head -1|grep -q "200 OK"
    - docker stop {{appname}} && docker rm --force {{appname}}
  
  
deploy:
  stage: deploy
  only:
    refs:
       - main
  script:
    - docker login --username $DOCKERIMAGES_USER --password $DOCKERIMAGES_PASS https://dockerimages.fhcrc.org
    - docker push dockerimages.fhcrc.org/{{appname}}:latest
    - sleep 15
    - rancher-v0.6.2/rancher --url https://ponderosa.fhcrc.org --access-key $RANCHERAPI_KEY --secret-key $RANCHERAPI_SECRET up -d --pull --force-upgrade --confirm-upgrade --stack {{appname}} --file docker-compose.yml --rancher-file rancher-compose.yml
  
"""

rancher_c = """version: '2'
services:
  {{appname}}:
    scale: 1
    start_on_create: true
"""

docker_c = """version: '2'
services:
  {{appname}}:
    image: dockerimages.fhcrc.org/{{appname}}:latest

    labels:
      io.rancher.container.pull_image: always

    restart: always
"""

if __name__ == "__main__":
    p = optparse.OptionParser()
    p.add_option('-n', '--name',  action='store', type='string', dest='appname', help='[REQUIRED] What is the shortname of this application')
    parms, args = p.parse_args()
    if not parms.appname:
        print("\nMissing application name parameter (-n or --name)\n")
        sys.exit(1)
    main(parms.appname.replace(' ',''))
