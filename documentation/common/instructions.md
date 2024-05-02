# Development Environment

Installing developement environment takes lot of time and there are many
steps to follow and many steps that can go wrong. If you are not familiar
with Docker and other techniques used you can expect spending more or less 3
hours installing. We really hope that documentation clears things up even a
bit. Happy installing.


## Install Docker

First, you need to have Docker and Docker Compose installed on your system. 

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)


### Getting docker from your distribution

You most probably want to install docker directly from your distribution.
Certainly this project doesn't need the latest version of Docker so you may
be better off with more tested and stable one. Installation is also simpler
and less risky.

Debian and Ubuntu (the only command needed, run as root):
```
apt-get install docker-compose
```

Note that older versions of docker make use of `docker-compose` instead of
`docker compose`. Functionality is pretty much the same and they are
interchangeable in examples of the documentation.

## Setting up the environment

### Clone

Just clone the repository and navigate your terminal to the root of it.


### Environment variables

Enviroment variables must be set correctly in `/.env` -file before building
docker containers.

It's good starting point to make copy of [`example.env`](example.env) to the
root of the project (next to `README.md`):
```
cp documentation/common/example.env .env
```
Then just open the `.env` -file and carefully examine and modify the file
contents according the instructions and the
[Environment variable docs](environment_variables.md).


### Build the containers
After docker is installed and environment variables are set correctly it's
time to build the containers. Note that in the first time building will take
considerable amount of time as container images needs to be fetched from the
internet and prepared. Reasonable estimate is around 10-20min.

```
docker compose build
```
It's good idea to run this periodically as container images gets upgrades.
Also after making chages to `Dockerfile` or `docker-compose.yml` containers
should be rebuild.


## Running the app

If everything went well so far you can start containers. Please note that in
the first time this will take quite much time as all migrations needs to be
pushed to the database.

### Start containers up:
```
docker compose up
```
Append `-d` switch for detached mode meaning that execution returns to
terminal and containers keep running on background.

Append `--build` switch to build the containers before starting them. This
is essentially same as running `docker compose build` just before.


After a while app should be accessible with browser. At the address
[localhost:8000](http://localhost:8000), you should see the MammalBase app
running. You can also visit phpMyAdmin at
[localhost:8001](http://localhost:8001) to see and modify the databases.

If the website doesn't show up wait some time or check the logs. Most likely
the service just hasn't started yet. Startup can take something like 5-30sec.

You can make changes to the Django app in real time when the containers are
running. The [`/app`](../../app) directory has been binded to the web
container so that all the changes to the host machine's `/app`
directory are also made in the container.

### Shutdown containers:
```
docker compose down
```


## Finalizing the Environment

### Setting up users

The `initialize.py`creates superuser with username and password from the environment variables. This file is run when the container is started.

Running command while containers are running
```
docker compose exec web python manage.py create_users
```
creates users defined in [user.csv](./../app/mb/management/commands/users.csv ) file. It contain kari's user and orcid. Now importing files from kari's examples is possible without changing the orcids.

This command also creates groups `data_admin`and `data_contributor`. You can add users to these groups in the admin page.

### Setting up database

The database is created and migrated when the containers are started.
Seeding the database with data is done by running the following command:
``` 
docker compose exec web python manage.py seed_db
```
You have to add the sql files to the [sql_files](./../app/mb/management/commands/sql_files) directory. The files should be named in the following format: `table_name.sql` or `name.sql.zip`.


## Basic commands

### View all logs:
```
docker compose logs
```
See `docker compose logs --help` for details.


### Follow logs as they appear:
```
docker compose logs -f
```


### Follow log of invidual container:
```
docker compose logs -f <container> 
```


### Shutdown containers and remove the volumes
```
docker compose down -v
```
In the case of wanting to also remove the volumes (meaning that
the **database will be reset**).


## Other useful commands

### List running containers:

```
docker ps
```
By knowing name or id you can do actions to certain container. It's not
guaranteed that names are same in different setups.


### Execute commands inside the container:

```
docker exec <container> <command> ...
```
Runs `<command> ...` inside the `<container>`. Container needs to be running
this to work. See `docker exec --help` for details.


### Check out local environment inside container:
```
docker exec mammalbase_web_1 sh -c export
``` 


### Open shell inside container:
```
docker exec -it mammalbase_web_1 bash
```
Note `-it` switch. It's needed for interactive commands.


### Generate migrations inside Django container:
```
docker exec mammalbase_web_1 python manage.py makemigrations
```


### Push migrations to the database:
```
docker exec mammalbase_web_1 python manage.py migrate
```

Note that changes in source tree causes developement server to restart.
See more in [Django docs](https://docs.djangoproject.com/en/3.2/).

Please note, that currently the django application makes migrations and
migrates the database every time the django container is started. If this
proves to be cumbersome the lines can be commented out in
[`entrypoint.sh`](./../app/scripts/entrypoint.sh) and commands above run
manually.
