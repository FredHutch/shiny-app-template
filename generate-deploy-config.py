#!/usr/bin/env python3

import argparse
import os
import sys 

def main(args):
    if "_" in args['name']:
        print("Error: App name cannot contain underscores")
        sys.exit(1)

    if not args['fqdn'].endswith('.fredhutch.org') and \
      not args['fqdn'].endswith('.fhcrc.org'):
        print("Error: FQDN must end with .fredhutch.org or .fhcrc.org")
        sys.exit(1)

    print("\nCreating configs for %s\n" % args['name']) 
    
    if os.path.exists('.gitlab-ci.yml') and not args['overwrite']:
        print("Error: .gitlab-ci.yml already exists. Use -o to overwrite.")
        sys.exit(1)

    with open('.gitlab-ci.yml', 'w') as fc:
      fc.write(gitlab_c.format(**args))

    if os.path.exists('docker-compose.yml') and not args['overwrite']:
        print("Error: docker-compose.yml already exists. Use -o to overwrite.")
        sys.exit(1)

    with open("docker-compose.yml", "w") as fc:
      fc.write(docker_c.format(**args))

    if args['external']:
      if not args['no_websockets']:
        args['websockets'] = websockets_c
      else:
        args['websockets'] = ""
      if args['auth_file_path']:
        args['auth'] = auth_c.format(**args)
      else:
        args['auth'] = ""
      if args['fqdn'].endswith(".fredhutch.org"):
        args['org'] = "fredhutch"
      elif args['fqdn'].endswith(".fhcrc.org"):
        args['org'] = "fhcrc"

      conf_file = f"{args['fqdn']}.conf"
      if os.path.exists(conf_file) and not args['overwrite']:
        print(f"Error: {conf_file} already exists. Use -o to overwrite.")
        sys.exit(1)

      with open(conf_file, "w") as fc:
        fc.write(nginx_c.format(**args))

gitlab_c = """
variables:
  CI_DEBUG_SERVICES: "true"

before_script:
  - apk update
  - apk --no-cache add py3-pip python3 curl
  - pip3 install pyyaml
  - curl -O https://raw.githubusercontent.com/FredHutch/swarm-build-helper/main/build_helper.py 
  # below is from https://stackoverflow.com/a/65810302/470769
  - mkdir -p $HOME/.docker
  - echo $DOCKER_AUTH_CONFIG > $HOME/.docker/config.json
  - set -x

stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - docker build -t sc-registry.fredhutch.org/{name}:test .
    - docker push sc-registry.fredhutch.org/{name}:test

test:
  stage: test
  services: 
    - name: sc-registry.fredhutch.org/{name}:test
      alias: {name}
  script:
    - sleep 15 && curl -sI  http://{name}:{port}  |head -1|grep -q "200 OK"

deploy:
  stage: deploy
  only:
    refs:
        - main
  script:
    - docker tag sc-registry.fredhutch.org/{name}:test sc-registry.fredhutch.org/{name}:latest
    - docker push sc-registry.fredhutch.org/{name}:latest
    - sleep 15
    - echo $SC_SWARM_CICD_SSH_KEY | base64 -d > ./sc_swarm_cicd_ssh_key
    - chmod 0400 ./sc_swarm_cicd_ssh_key
    - python3 build_helper.py docker-compose.yml | ssh -i ./sc_swarm_cicd_ssh_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@sc-swarm-mgr.fhcrc.org docker stack deploy --with-registry-auth -c - {name}
""".strip()


docker_c = """
version: '3.3'
services:
  {name}:
    image: sc-registry.fredhutch.org/{name}:latest
    networks:
      - proxy
    deploy:
      restart_policy:
        condition: on-failure
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.{name}.rule=Host(`{fqdn}`)"
        - "traefik.http.routers.{name}-secured.rule=Host(`{fqdn}`)"
        - "traefik.http.routers.{name}.entrypoints=web,web-secured"
        - "traefik.http.services.{name}.loadbalancer.server.port={port}" # it seems you always need to give traefik a port so it 'notices' the service
        - "traefik.http.routers.{name}.tls=true"

networks:
  proxy:
    external: true
""".strip()


nginx_c = """
server {{
    ssl_certificate /etc/nginx/certs/{org}.org.crt;
    ssl_certificate_key /etc/nginx/certs/{org}.org.key;
    listen 443 ssl;
    # this is the FQDN of the app - CNAME in infoblox external zone should point to swarm-proxy.fhcrc.org
    server_name {fqdn};

    ssl on;

    location / {{
        {websockets}
        # the thing we are proxying already has ssl turned on:
        proxy_ssl_server_name on;
        proxy_pass https://{fqdn};
        {auth}
    }}
}}
""".strip()

websockets_c = """
        # if we are proxying something that uses websockets (like a shiny app)
        # then we need the following 3 lines:
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        # when app uses runApp() (not Shiny Server)
        # you must set proxy_read_timeout (as below). See
        # https://support.posit.co/hc/en-us/articles/213733868-Running-Shiny-Server-with-a-Proxy
        # TODO - uncomment this line if necessary:
        # proxy_read_timeout 20d;
""".strip()

auth_c = """
        auth_basic "ShinyApp";
        auth_basic_user_file "/etc/nginx/auth_repos/{github_repo}/{auth_file_path}";
""".strip()

if __name__ == "__main__":
    p = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter,
      description='generate deploy config files for a new app',
      epilog="""You will probably need to tweak these files manually.
You will need to copy the nginx config to swarm-proxy:/etc/nginx/conf.d/
if this is an external facing app (and restart nginx).
If app uses basic auth, you'll need to clone the app repo
in swarm-proxy:/etc/nginx/auth_repos.""")
    p.add_argument('-n', '--name',
      action='store',
      required=True,
      help='What is the shortname of this application')
    p.add_argument('-f', '--fqdn',
      action='store', help="fully-qualified domain name", default="NAME.fredhutch.org")
    p.add_argument('-p', '--port',
      action='store', default=3838, type=int, help="port exposed by default service")
    p.add_argument('-g', '--github-repo', default='NAME',
      action='store', help="github repo for this app (repo name only, omit https://github.com/FredHutch/)")
    p.add_argument('-a', '--auth-file-path',
      action='store', help="relative path to auth file (if using basic auth). Example: system/auth",
      )
    p.add_argument('-o', '--overwrite', action='store_true',
      help="overwrite existing files", default=False)
    p.add_argument('-e', '--external', action='store_true', default=False,
      help="App will be deployed externally. Generates proxy nginx config.")
    p.add_argument('-w', '--no-websockets', action='store_true', help='does not use websockets, only needed if EXTERNAL==True')
    args = p.parse_args()
    if args.github_repo == 'NAME':
        args.github_repo = args.name
    if args.fqdn == 'NAME.fredhutch.org':
        args.fqdn = f"{args.name}.fredhutch.org"
    # import IPython; IPython.embed();sys.exit(1)
    main(vars(args))
