# Data architecture

## Database

The application uses a `MariaDB` database to store data. The database tables
are managed by Django's ORM. The application is divided into several
subapplications, each of which contains files related to a specific feature
of the application. 


## Models

### MammalBase

Most of the MammalBase related models are defined in the `mb` subpackage in
[`/app/mb/models`](../../../app/mb/models) directory. 

The directory contains files for different types of models by category.
Order is kept by the subpackage `mb.models` meaning that all models are
impoted in `__init__.py`. This how models can be imported elsewhere directly
from subpackage like `from mb.models import ...`. Failing to do so may
result in duplicates of models, failing migrations
and **hard to track down errors**.

All the models in `mb` inherit from `BaseModel` which is defined in
[`/app/mb/models/base_model.py`](../../../app/mb/models/base_model.py) file.
`BaseModel` also makes use of  `simple_history` extension to keep track of
changes in the database. 


### TDWG (Taxonomic Databases Working Group)

The [`/app/tdwg`](../../../app/tdwg) directory contains `Taxon` model that
follows TDWG (Taxonomic Databases Working Group) standards.


### More models

There are even more models defined in:
- [`/app/itis/models.py`](../../../app/itis/models.py)
- [`/app/exports/models.py`](../../../app/exports/models.py)
