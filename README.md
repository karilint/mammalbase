![Django](https://github.com/karilint/mammalbase/actions/workflows/django.yml/badge.svg)
# MammalBase

MammalBase is a database of recent mammals. The main focus of this database is the Trait Data, Measurements and Diets of the species in class Mammalia. For dietary information, we also provide Proximate Analysis data for several diet items.

# Documentation

Documentation has been compiled behind the documentation directory. There, the structure of the code, Django model objects used in the code, and, for example, the logic of import and export operations are explained. Various scripts related to the use of MammalBase are also described in their own documents.

Below are a few direct links to key instructions.

## Developing Environment

### Setting up

[Instructions](documentation/common/instructions.md)
- Setting up the development environment and other important aspects in development work

[Master Habitats Script](documentation/scripts/master_habitat_scripts.md)
- Retrieval of Master Habitats using a script

### Testing
[Testing Guide](documentation/common/testing.md)
- Instructions for testing the software

### Deployment
[Deploying](documentation/common/deploy.md)
- Instructions how put code to staging and production.

### Using Celery to run tasks in the background
[Celery instructions](documentation/common/celery.md)
- Background tasks in the software are executed with the Celery library.


## The Project

[Architecture](documentation/mammalbase/arch/architecture.md)
- Overview of the software architecture

[Data Architecture](documentation/mammalbase/arch/data-architecture.md)
- Overview of data architecture

[Models](documentation/mammalbase/models/)
- Models used in MammalBase

[Features](documentation/mammalbase/features/)
- Current features of MammalBase (e.g. importing and exporting tsv-files)
[Creating Tabs](documentation/mammalbase/features/creating_tabs.md)
- How to add a new tab and related view

