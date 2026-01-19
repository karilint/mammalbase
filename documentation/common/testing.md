# Testing Guide

## Unit tests

### Running tests

To run all the existing unit tests, run:

```
docker exec mammalbase_web_1 python manage.py test
```

Use the Django test runner so the app registry is initialized and installed
apps are discovered correctly. This avoids import issues when tests use app
packages such as `mb`, `imports`, `tdwg`, and `exports`.

Run a specific test file by adding the path to the file:

```
docker exec mammalbase_web_1 python manage.py test tests.[folder].[test_file]
```
Replace [folder] and [test_file] with the correct path to the test file.

The tests may not work locally before the database privileges are set for
Django. Once docker containers are running, run this command:

```
docker exec -it mammalbase_db_1 mysql -u root -p
```

Enter the DB_ROOT_PASS from `.env` -file

Once in MySQL, run this command to grant privileges:

```
GRANT ALL PRIVILEGES ON *.* TO 'mb_dev'@'%';
```
- NOTE: Database name (mb_dev in this case) should be the same as in the .env file.

Hit <kbd>Ctrl</kbd>+<kbd>D</kbd> or give `QUIT` -command to exit MySQL.
Tests should work now.

### Creating and/or modifying tests

Test files are located in `/app/tests`.

When adding or updating tests, import models and utilities from the installed
app packages (for example `mb.models`, `imports.importers`, `exports.models`,
and `tdwg.models`) rather than legacy or unscoped module paths. This keeps
imports aligned with the current package layout and Django app registry.

### Test coverage

You can create test coverage report by first installing coverage.py to the container:
```
docker exec mammalbase_web_1 pip install coverage
```
Run tests with:
```
docker exec mammalbase_web_1 coverage run --source='.' manage.py test
```

To see the report run:
```
docker exec mammalbase_web_1 coverage report
```
For html report run:
```
docker exec mammalbase_web_1 coverage html
```

### Pylint

Pylint can be run in the containers by using the following command:
```
docker exec mammalbase_web_1 scripts/pylint.sh 
```
This tests whole source tree. By appending paths to the end of command line
you can test only chosen directories:
```
docker exec mammalbase_web_1 scripts/pylint.sh urls mb/models
```

The script will install pylint and pylint_django if not yet installed.

If you want to run pylint outside the container you will need to install
pylint on your own system.
