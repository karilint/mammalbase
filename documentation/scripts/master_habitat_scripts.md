# Master habitats script
The Master Habitats Script is a Django management command designed to add officially defined biomes to the `master_habitat` table in the database.
It parses CSV files containing biome data and creates corresponding entries in the database.

The script is located at `app/mb/management/commands/master_habitat_script.py` within the Django project.
The CSV files containing biome data are stored in the `app/mb/management/commands/habitat_csv` directory.

## Field Descriptions

1. `reference` This is a foreign key field that creates a many-to-one relationship with the MasterReference

2. `parent` This is a foreign key field that creates a many-to-one relationship with the same MasterHabitat model. This allows a MasterHabitat object to be a "child" of another MasterHabitat object, forming a hierarchical structure. Only applicable in Olson Biomes.

3. `name` This is a character field containing the name of the habitat/biome.

4. `code` This is a positive small integer field containing a biome classification code. Eco code in Olson Biomes, biome code in WWF Biomes and IIASA code in Holdridge Biomes.

5. `group` This is a character field containing the group or category of the biome (there are multiple instances of fields of the same name existing in different groups). Only applicable in Olson Biomes.

## Process of Adding Biomes

1. Adding Olson Biomes

    The script reads Olson biome data from the CSV file biomes_olson_1983.csv.
    It iterates through each row of the CSV file and creates MasterHabitat objects for each biome.
    Biomes are associated with a reference and a parent habitat if applicable.

2. Adding WWF Biomes

    The script reads WWF biome data from the CSV file biomes_wwf.csv.
    It iterates through each row of the CSV file and creates MasterHabitat objects for each biome.
    Biomes are associated with a reference.

3. Adding Holdridge Biomes

    The script reads Holdridge biome data from the CSV file biomes_holdridge.csv.
    It iterates through each row of the CSV file and creates MasterHabitat objects for each biome.
    Biomes are associated with a reference.
   
## Instructions
To run the command:
1. Make sure that web container is running. Refer
  [DevEnv](../common/instructions.md) instructions for details.
2. Run the Django command:
```
docker exec mammalbase_web_1 python manage.py master_habitat_script
```
