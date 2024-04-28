# Development Environment

## Install Docker

First, you need to have Docker and Docker Compose installed on your system. 

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)


### Getting docker from your distribution

You most probably want to install docker directly from your distribution.
Certainly this project doesn't need the latest version so you may be better
off with more tested and stable one. Installation is also simpler and less
risky.

Debian and Ubuntu (the only command needed, run as root):
```
apt-get install docker-compose
```

Note that older versions of docker make use of `docker-compose` instead of
`docker compose`. Functionality is pretty much the same and they are
interchangeable in examples of the documentation.


## Environment variables

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


## Running the environment

To start the environment, you have to run the following command in the root
the repository.  
```
docker compose up -d --build
```
- NOTE: Running this command without the `-d` tag will show logs in the same
  terminal.
- NOTE 2: `--build` will create a new container and is unnecessary unless
  something has been changed in the Dockerfile or `docker-compose.yml` file.

Now if you go to [localhost:8000](http://localhost:8000), you should see the
MammalBase app running. You can also go to phpMyAdmin at
[localhost:8001](http://localhost:8001) to see or modify the created database.
If the website doesn't show up wait some time or check the logs. Most likely
the service just hasn't started yet. Startup can take something like 5-30sec.
Or even more on first run as the app runs through all migrations.

You can make changes to the django app in real time when the containers are
running. The [`/app`](../../app) directory has been binded to the web
container so that all the changes to the host machine's [`/app`](../../app)
directory are also made in the container.


## Basic commands

### Start up containers:
```
docker compose up
```


### View all logs:
```
docker compose logs
```


### Follow logs as they appear:
```
docker compose logs -f
```


### Follow log of invidual container:
```
docker compose logs -f <container> 
```


### Shutdown containers:
```
docker compose down
```


### Shutdown containers and remove the volumes
```
docker compose down -v
```
In the case of wanting to also remove the volumes (meaning that the database
will be reset).


## Other useful commands

### List running containers:

```
docker ps
```
By knowing name or id you can do actions to certain container. It's not
guaranteed that names are same in different setups.


### Execute commands inside the container:

```
docker exec <container> <command>
```
Container needs to be running this to work.


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
