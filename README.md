# Shiny App Template

This repository contains an example Shiny application can be used as the starting point for new applications that you would like to containerize and deploy/update via an automated pipeline.

You will need a pick a short name for your application. The name that you pick will be the name of the Docker image and application that is created. The in documentation below the name of application is ***"myshinyapp"*** (names shouldn't have any spaces or any special characters (stick to a-z, A-Z and 0-9).

**1.** Clone this repository to your workstation giving it the short name of your application:

```bash
$ git clone https://github.com/fredhutch/shiny-app-template myshinyapp

Cloning into 'myshinyapp'...
remote: Counting objects: 14, done.
remote: Compressing objects: 100% (13/13), done.
remote: Total 14 (delta 3), reused 12 (delta 1), pack-reused 0
Unpacking objects: 100% (14/14), done.
Checking connectivity... done.
```

**2.** Remove the hidden '.git' directory and reinitialize as a new repository:

```bash
$ cd myshinyapp
$ rm -rf .git
$ git init

Initialized empty Git repository in /home/rmcdermo/myshinyapp/.git/
```

**3.** Add and commit the existing files:

```bash
$ echo "# myshinyapp" > README.md
$ git add .
$ git commit -m "initial commit"
[master (root-commit) 4af5f0b] initial commit
 6 files changed, 136 insertions(+)
 create mode 100644 Dockerfile
 create mode 100644 README.md
 create mode 100644 app/server.R
 create mode 100644 app/start.R
 create mode 100644 app/ui.R
 create mode 100644 generate-deploy-config.py
```

**4.** Create a new empty Git repository on GitHub using the short name of your application (myshinyapp in this example).  In this example, we'd create the https://github.com/fredhutch/myshinyapp repository. During creation. ***Don't*** initialize the repository.

**5.** Add a git remote on the local git repository connecting it to the newly created GitHub repository:

```bash
$ git remote add origin https://github.com/FredHutch/myshinyapp.git

$ git push -u origin master
```

**6.** Develop your application by replacing the code contained in the 'app/ui.R' and 'app/server.R' source files with your application code. Remember to commit and push your code to save your work.

**7.** Test your container locally to make sure that it builds and your application runs.

Build the Docker image:

```bash
$ docker build -t myshinyapp:latest .
```

If the build fails due to a missing R dependency, add that dependency to the [fredhutch/r-shiny-base](https://github.com/FredHutch/r-shiny-base/blob/master/installRpackages.R) "installRpackages.R" source file and wait till the image has been built and pushed to the [r-shiny-base](https://hub.docker.com/r/fredhutch/r-shiny-base/) Docker repository (automated process).

If the build fails due to a missing dependency in the operating system, then add that dependency to the "Dockerfile" (ex: RUN apt-get install -y mydependency).

**8.** Run the container locally to ensure that your application is working correctly.

```bash
$ docker run -d --name myshinyapp -p 7777:7777 myshinyapp:latest

175d95092d4fa71eb8bc7de76d80d70eeb23d8a2fb47ac10d81ebc2699af8335
```

Now check to see if your container is running:

```bash
$ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
175d95092d4f        myshinyapp          "/bin/sh -c 'Rscri..."   3 seconds ago       Up 2 seconds        0.0.0.0:7777->7777/tcp   myshinyapp
```

If your app is not running, look at the logs to see if you can determine what is wrong (missing dependency, etc...):

```bash
$ docker logs myshinyapp
```

After the container is running, you can point your web browser at http://localhost:7777 to test that your application is functioning correctly (curl http://localhost:7777).

When you have confirmed that the application is working correctly, you can stop it and remove the image from your workstation if you desire:

```bash
$ docker stop myshinyapp
$ docker rm myshinyapp
$ docker rmi myshinyapp:latest
```

**9.** When everything is working as it should, contact Scientific Computing at scicomp@fredhutch.org to start the process of deploying your application on a server so others can access it.

**10.** IT/devops staff, you can use the "generate-deploy-config.py" script contained in this repository to generate the configurations needed to build an automated deployment pipeline. While in the repository, run:

```bash
$ python generate-deploy-config.py --name myshinyapp

Creating configs for myshinyapp
```

The above command will create the following three files in the repository using the provided (-n or --name) short name of the application.

- docker-compose.yml
- rancher-compose.yml
- circle.yml