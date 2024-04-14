# Testing Guide

## Unit tests

### Running tests

To run all the existing unit tests, run:

```bash
docker exec mammalbase-web-1 bash -c "python manage.py test"
```

Run a specific test file by adding the path to the file:

```bash
docker exec mammalbase-web-1 bash -c "python manage.py test tests.[folder].[test_file]"
```
Replace [folder] and [test_file] with the correct path to the test file.

The tests may not work locally before the database privileges are set for Django. Once docker containers are running, run this command:

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
docker exec mammalbase-web-1 bash -c "pip install coverage"
```
Run tests with:
```bash
docker exec mammalbase-web-1 bash -c "coverage run --source='.' manage.py test"
```

To see the report run:
```bash
docker exec mammalbase-web-1 bash -c "coverage report"
```
For html report run:
```bash
docker exec mammalbase-web-1 bash -c "coverage html"
```

### Pylint

Pylint can be run in the containers by using the following command:
```sh
docker exec <container> scripts/pylint.sh 
```
Thist test whole source tree. By appending paths to the end you can test
only chosen directories.

If you want to run pylint outside the container you will need to install
pylint on your own system.
