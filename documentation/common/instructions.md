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
`docker compose`. Functionality is pretty much the same and interchangeable
in examples of the documentation.


## Environment variables

Create a `.env` file in the root of the repository and write needed
environment variables to it. You can take the [Example .env](example.env):
```
cp documentation/common/example.env .env
```
Then just open the `.env` -file in text editor and fill out at least the
marked varibles according to the 
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

Now if you go to [localhost:8000](localhost:8000), you should see the app
running. You can also go to [localhost:8001](localhost:8001) to see or modify
the created database. If the website doesn't show up, check the logs. Most
likely the service just hasn't started yet. 

You can make changes to the django app in real time when the containers are
running. The [`/app`](../../app) directory has been binded to the web
container so that all the changes to the host machine's [`/app`](../../app)
directory are also made in the container. 

To see logs you can run this command:
```
docker compose logs -f
```

You can also specify a container if you only want to see specific logs:
```
docker compose logs -f <container> 
```
If you want to shutdown the containers, you can run this command:
```
docker compose down
```
In the case of wanting to also remove the volumes (meaning that the database
will be reset), you can run:
```
docker compose down -v
```

### Other useful commands

You can list running container ids by following command (This is usefull if
you need for example execute some command inside certain container):
```
docker ps
```

You can execute commands inside the container by running:
```
docker exec <container> <command>
```
For checking out local environment inside container:
```
docker exec mammalbase_web_1 sh -c export
``` 

Open hell inside container:
```
docker exec -it mammalbase_web_1 bash
```

For example, if you need to make migrations inside django, you can run:
```
docker exec mammalbase_web_1 python manage.py makemigrations
```

To migrate the database:
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
