![A Python Project Repo](https://www.python.org/static/community_logos/python-logo-master-v3-TM-flattened.png)

---

# StuCo App

A Web Application created with the Django Framework for the Carnegie Mellon Student Courses
Course **98010** - Intro to Submission Grappling.

###### This project was created with [Cookiecutter](https://github.com/audreyr/cookiecutter).

---

## Powered by Poetry

Projects created with the Project Generator now utilize Poetry
[https://python-poetry.org](https://python-poetry.org)
to manage a virtual environment and the project dependencies. The included Makefile will install poetry for you automatically you don't already have it installed.

---

## Pre-requisite Requirements:

- Projects created with the **Project Generator** aka **SPG** should have the following tools installed in order to obtain the maximum feature set :

  - The **python** command (note there is no '3' at the end) must be available and point to a Version 3 or greater of Python.
  - **git** should be installed and be at **least version 2.28** so that the default branch can be set as **main** in keeping with the current times. Additionally, you should set your default branch to **main** using the command:
    ```
    git config --global init.defaultBranch main
    ```
    - For details about this new feature in git [see this post](https://www.kunal-chowdhury.com/2020/07/git-default-branch.html)
  - **Docker** should be installed. While use of Docker is not required for developing and testing, it **is** required in order to generate the Docker Image which is a part of the development flow.
  - The **make** command should be installed and available in your environment.
  - While it is by no means required, it is highly recommended that you use **Visual Studio Code** as your IDE if you don't already have a favorite - there are many nice integrations that get set up for you automatically in our projects.

---

## Development

#### Ease your Development Process with the Make Command

- This project is built with a Makefile that provides many convenience commands for you to speed your productivity. In order to obtain the benefits that the Makefile provides, you need to ensure that you have an environment setup that includes the **make** command. All **make** commands should be executed from within the root directory of the project. Where possible, the Makefile has been crafted to also build any dependencies for each command.

#### List available make targets

- To list the set of make targets you can simply type the command make with no arguments. This will **not** build anything - it will simply list the available targets:
  ```
  make
  ```

#### Validate your local environment and Run tests

- All Projects created with the STO Project Generator are designed such that you should be able to simply clone a repo, cd into the root directory of the project, and execute the command:
  ```
  make test
  ```
- This will (as a side effect) create a python virtual environment for you named **.venv** in the project's root directory (if it doesn't already exist), create a local **Docker** image for the project (if it doesn't already exist), and run any existing tests.
- You may "activate" this virtual environment manually any time you wish (if you don't want to use **poetry**) by executing the command:
  ```
  source .venv/bin/activate
  ```

#### Create a local version of the Docker Image

- This project is tooled for Docker-based development. While development with Docker is fully supported, it is **not** required for project development - it is simply supported as a convenience.

- There are a variety of **make** commands which will result in a local **Docker** image being created for you, but you may always explicitly create this image with the following instructions.

- After cloning the project, make sure that you are in the project root directory: **stuco_app** and then execute the command:

  ```
  make local-docker-image
  ```

- This will create a new local version of the docker image that is built in local mode and will have several development tools pre-installed for you.

_Note:_ executing this command will create a local file in the hidden directory: **.spg** named **.local-docker-image** (a "hidden file"). This file is used to avoid having to re-create the local image each time you want to execute one of the other make commands that utilize the image. Should you find yourself wanting to force a re-build of the local image, you should explicitly delete the file **.spg/.local-docker-image**

**OR**

- you could simply perform the command:

  ```
  make clean
  ```

- and then perform the command:

```
make local-docker-image
```

#### Work inside the Docker Image

- To run the local docker image and open a bash shell:
  ```
  make work
  ```

#### VS Code Development

- This project has a **.devcontainer** subdirectory which allows **VS Code** users to re-open in remote container (if they have the remote-containers plugin installed). Once re-opened in a remote container, the Terminal will actually be running inside the local docker image which has a zshell (and oh-my-zsh pre-installed). To start a oh-my-zsh session, simply type the command: **zsh** in the Terminal window. To activate the local python virtual environment you can type the command:
  ```
    source .venv/bin/activate
  ```

**or**

- you could use [**poetry** https://python-poetry.org](https://python-poetry.org/) by prefixing any command that would utilze python with:

  ```
    poetry run
  ```

- for example:
  ```
    poetry run python -m pip list
  ```

#### Running Unit Tests

- To run the unit tests only, simply use the make test command with the additional arguments **type=unit**:
  ```
  make test type=unit
  ```

#### Running Integration Tests

- To run the integration tests only, simply use the make test command with the additional arguments **type=integration**:
  ```
  make test type=integration
  ```

#### Running a Suite of Static Analysis Tests

- To run all of the available static analysis checks, simply use the command"
  ```
   make check
  ```

#### Generate Documentation for this Repo

- To generate the documentation, simply use the command"

  ```
   make docs
  ```

- To generate the documentation **and** start up a server to serve the documentation, use the command"

  ```
   make docs-serve
  ```

###### The server will listen at [http://localhost:8000](http://localhost:8000)

---

###### The Make commands are now backed by the python duty package: [https://pawamoy.github.io/duty/usage/](https://pawamoy.github.io/duty/usage/)

You can see what's actually being run (and / or modify what gets run) by viewing the file **.spg/duties.py**.

---
2024
