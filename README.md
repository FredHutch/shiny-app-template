# Shiny App Template

This repository contains an example Shiny application can be used as the starting point for new applications that you would like to containerize and deploy/update via an automated pipeline.

You will need a pick a short name for your application. The name that you pick will be the name of the Docker image and application that is created. The in documentation below the name of application is ***"myshinyapp"*** (names shouldn't have any spaces or any special characters (stick to a-z, A-Z and 0-9).

**1. Clone this repository to your workstation giving it the short name of your application:**

```bash
$ git clone https://github.com/fredhutch/shiny-app-template myshinyapp

Cloning into 'myshinyapp'...
remote: Counting objects: 14, done.
remote: Compressing objects: 100% (13/13), done.
remote: Total 14 (delta 3), reused 12 (delta 1), pack-reused 0
Unpacking objects: 100% (14/14), done.
Checking connectivity... done.
```

**2. Remove the hidden '.git' directory and reinitialize as a new repository:**

```bash
$ cd myshinyapp
$ rm -rf .git
$ git init

Initialized empty Git repository in /home/rmcdermo/myshinyapp/.git/
```

**3. Add and commit the existing files:**

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

**4. Create a new empty Git repository on GitHub using the short name of your application (myshinyapp in this example).  In this example, we'd create the https://github.com/fredhutch/myshinyapp repository. During creation. *Don't* initialize the repository**

**5. Add a git remote on the local git repository connecting it to the newly created GitHub repository:

```bash
$ git remote add origin https://github.com/FredHutch/myshinyapp.git

$ git push -u origin master
```