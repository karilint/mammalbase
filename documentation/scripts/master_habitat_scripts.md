# Master habitats script
The script is used to add officially defined biomes to the `master_habitat` table.
## Instructions
The script is located in `app/scripts` and the csv files are located in the `app/scripts/habitat_csv` directory.
To run the script:
1. Start the Docker environment with the command:
```
docker compose up -d
```
2. Open python/django shell with the command:
```
docker compose exec web python manage.py shell 
```
3. Save the script path to a variable with the command:
```
script_path = 'scripts/master_habitats.py'
```
4. Execute the script with the command:
```
exec(open(script_path).read(), {'__file__': script_path})
```
- NOTE: Running the script multiple times will add duplicate habitats to the table.
