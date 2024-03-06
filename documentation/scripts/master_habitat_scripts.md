# Master habitats script
The Master Habitats Script is a Django management command designed to add officially defined biomes to the `master_habitat` table in the database.
It parses CSV files containing biome data and creates corresponding entries in the database.

The script is located at `app/mb/management/commands/master_habitat_script.py` within the Django project.
The CSV files containing biome data are stored in the `app/mb/management/commands/habitat_csv` directory.
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
1. Start the Docker environment with the command:
```
docker compose up -d
```
2. Run the Django command:
```
docker compose exec web python manage.py master_habitat_script
```
