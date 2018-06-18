import optparse
import sys 

def main(appname):
    print("\nCreating configs for %s\n" % appname) 
    
    fc = open('circle.yml', 'w')
    fc.write(circle_c.replace('{{appname}}', appname))
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

circle_c = """machine:
  services:
    - docker
  environment:
    BUILD_HOST: circle-build01.fhcrc.org

dependencies:
  override:
    - curl -LO https://releases.rancher.com/cli/v0.6.2/rancher-linux-amd64-v0.6.2.tar.gz
    - tar zxf rancher-linux-amd64-v0.6.2.tar.gz
    - ls -lh
    - docker build -t dockerimages.fhcrc.org/{{appname}}:latest .

test:
  override:
    - docker run -d --name {{appname}} -p 7777:7777 dockerimages.fhcrc.org/{{appname}}:latest
    - sleep 15 && curl --retry 10 --retry-delay 5 -v http://${BUILD_HOST}:7777
    - docker stop {{appname}} && docker rm --force {{appname}}

deployment:
  prod:
    branch: master
    commands:
      - docker login --email fredhutch@fhcrc.org --username $DOCKERIMAGES_USER --password $DOCKERIMAGES_PASS https://dockerimages.fhcrc.org
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
