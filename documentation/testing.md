# Testing Guide

## Unit tests

### Running tests

To run all the existing unit tests, run:

```bash
docker exec mammalbase_web_1 bash -c "python manage.py test"
```

The tests may not work locally before the database privileges are set for Django. Once docker containers are running, run this command:
### Windows
```bash
docker-compose exec db mysql -u root -p
```
### Linux
```bash
docker compose exec db mysql -u root -p
```

Enter the DB_ROOT_PASS from env-file

Once in MySQL, run this command to grant privileges:

```bash
GRANT ALL PRIVILEGES ON *.* TO 'mb_dev'@'%';
```
- NOTE: Database name (mb_dev in this case) should be the same as in the .env file.  

Type ```QUIT``` to exit MySQL. Tests should work now.

### Creating and/or modifying tests

Test files are located in app/tests.  

### Test coverage

You can create test coverage report by first installing coverage.py to the container:
```bash
docker exec mammalbase_web_1 bash -c "pip install coverage"
```
Run tests with:
```bash
docker exec mammalbase_web_1 bash -c "coverage run --source='.' manage.py test"
```

To see the report run:
```bash
docker exec mammalbase_web_1 bash -c "coverage report"
```
For html report run:
```bash
docker exec mammalbase_web_1 bash -c "coverage html"
```
