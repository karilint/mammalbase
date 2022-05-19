# Testing Guide

## Alustava

## Unit tests

### Running tests

To run all the existing unit tests, run:

```
python manage.py test
```

The tests may not work locally before the database privileges are set for Django. Once docker containers are running, run this command:

```
docker-compose exec db mysql -uroot -p
```
Enter the DB_ROOT_PASSWORD ([Example .env](https://github.com/karilint/TaxonManager/blob/main/docs/environment_variables.md)), probably:

```
rootpassword
```

Once in MySQL, run this command to grant privileges:

```
GRANT ALL PRIVILEGES ON *.* TO 'django_tm'@'%';
```
Type ```QUIT``` to exit MySQL. Tests should work now.

### Creating and/or modifying tests

Test files are located in app/tests.  

## Cypress

### Running tests

At first, run this command in the root the repository:

```
npm install
```

It will install all the packages needed by cypress (inside the node_modules folder).

Then, to run all the existing Cypress tests, run this command:

```
npm run cypress:run
```

The Cypress tests are currently using test data from /app/front/fixtures/test.json. 
Once docker containers are running, data can be loaded by

```
docker-compose exec web python manage.py loaddata test.json"
```

Some cypress tests may not work properly unless the database is cleared before loading the test data.


### Creating and/or modifying tests

Test files are located in cypress/integration. 

To launch Cypress test runner, run this command: 

```
npm run cypress:open
```
