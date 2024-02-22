# Master habitats script
The script is used to add officially defined biomes to the `master_habitat` table.
## Instructions
The script has been created as a Django command and is located in `app/mb/management/commands` and the csv files are located in the `app/mb/management/commands/habitat_csv` directory.
To run the command:
1. Start the Docker environment with the command:
```
docker compose up -d
```
2. Run the Django command:
```
docker compose exec web python manage.py master_habitat_script
```
