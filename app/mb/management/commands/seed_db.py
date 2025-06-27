from django.core.management.base import BaseCommand
from django.db import connection
import os
import zipfile
import logging

class Command(BaseCommand):
    help = 'Seeds the database from specified SQL files'
    sql_files = []

    def handle(self, *args, **options):
        #search for sql files in the sql_files directory
        self.sql_files = [f for f in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sql_files')) if f.endswith('.sql') or f.endswith('.zip')]
        
        if not self.sql_files:
            self.stdout.write(self.style.WARNING('No SQL files found in the sql_files directory'))
            return
        
        for sql_file in sorted(self.sql_files):
            self.execute_sql_file(sql_file)
            self.stdout.write(self.style.SUCCESS(f'Successfully executed SQL file {sql_file}'))
            
        

    def execute_sql_file(self, sql_file_path):
        # Determine the path to SQL files
        base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sql_files')
        full_path = os.path.join(base_path, sql_file_path)

        # Check if the file is a ZIP archive
        if sql_file_path.endswith('.zip'):
            with zipfile.ZipFile(full_path, 'r') as zip_ref:
                # Extract all the files into a temporary directory
                zip_ref.extractall(base_path)
                # Assume there is one SQL file per ZIP for simplicity
                extracted_files = zip_ref.namelist()
                for file in extracted_files:
                    self.execute_individual_sql(os.path.join(base_path, file))
        else:
            self.execute_individual_sql(full_path)

    def execute_individual_sql(self, path):
        """Execute SQL statements from a file one by one."""
        logger = logging.getLogger(__name__)

        with open(path, "r", encoding="utf-8") as file:
            sql_script = file.read()

        statements = sql_script.split(";\n")
        with connection.cursor() as cursor:
            for statement in statements:
                stmt = statement.strip()
                if not stmt:
                    continue
                try:
                    cursor.execute(stmt + ";")
                except Exception as exc:
                    logger.error(
                        "Failed to execute SQL from %s: %s", path, stmt[:50], exc_info=exc
                    )
                    raise

