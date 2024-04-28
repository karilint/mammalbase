# Data architecture

The application uses a `MariaDB` database to store data. The database tables are managed by Django's ORM. The application is divided into several subapplications, each of which contains files related to a specific feature of the application. 

Most of the models are defined in the `mb` directory. The `mb` directory contains main files related to the main MammalBase application. All the `models` related to MammalBase are defined in this directory.

The `tdwg` directory contains `Taxon` model that follows TDWG (Taxonomic Databases Working Group) standards.

All the models in mb inherit from base_model which is defined in `models` directory. The `models` directory contains files for different types of models by category. All model must be imported to `models/__init__.py` 
file.

Project also uses `simple_history` extension to keep track of changes in the database. 

