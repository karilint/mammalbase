# Testing Guide

## Unit tests

### Running tests

To run all the existing unit tests, run:

```
docker exec mammalbase_web_1 bash -c "python manage.py test"
```

The tests may not work locally before the database privileges are set for Django. Once docker containers are running, run this command:

```
docker-compose exec db mysql -uroot -p
```
Enter the DB_ROOT_PASS from env-file

Once in MySQL, run this command to grant privileges:

```
GRANT ALL PRIVILEGES ON *.* TO 'django_tm'@'%';
```
Type ```QUIT``` to exit MySQL. Tests should work now.

### Creating and/or modifying tests

Test files are located in app/tests.  
