# Environment Variables

## Development environment

- DB_HOST is the host of the database (should be set to "db" because mariadb container is called that)
- DB_PORT is the port used by the database. (mariadb container uses the port 3306 so should be set as that)
- DB_NAME is the name of the database. 
- DB_USER is the name of the database user.
- DB_PASS is the password for the user. 
- DB_ROOT_PASS is the root password for the database. 
- EMAIL_BACKEND defines the email backend django will use. In development, it is usually set as `django.core.mail.backends.console.EmailBackend` so that the emails go to the logs/terminal.
- EMAIL_USER the email django uses. NOT NEEDED when using console emailbackend.
- EMAIL_PASS the password for the email. NOT NEEDED when using console emailbackend.
- ORCID_CLIENT_ID is client id for the orcid authentication. ORCID OAuth will not work without it. 
- ORCID_SECRET is secret for the orcid authentication. ORCID OAuth will not work without it.
- DJANGO_SUPERUSER_USERNAME is the username the django container uses to create a superuser at startup.
- DJANGO_SUPERUSER_PASSWORD is the password the django container uses to create a superuser at startup.
- DJANGO_SUPERUSER_EMAIL is the email the django container uses to create a superuser at startup.
- SITE_NAME is the name for the website. You can set it as "MammalBase".
- SITE_DOMAIN is the domain for the website. In development it can be set as "localhost:8000".
- UID is the ID of the user that Docker will try to run the application as. This is needed to give Docker the proper permissions. The user id can be found out using the following commands:
### Linux 
```bash
id -u <username>
```
### Windows
```bash
whoami /user
```

### Other variables (these don't need to be defined)

- SECRET_KEY is the secret key django will use. Django defaults to "development_key" if not set. 
- DEBUG defaults automatically to 1. However, if you want to run the django application without debugging on, you can set this to 0.
- ALLOWED_HOSTS defaults automatically to '*'. But if you want to define certain hosts, they need to seperated by `,`. For example, `127.0.0.1,localhost`.

 
 
