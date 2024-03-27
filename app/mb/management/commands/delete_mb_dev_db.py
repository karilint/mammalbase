import os
from django.core.management.base import BaseCommand
from django.db import connection,connections
from django.db.utils import OperationalError
import zipfile
import os
from time import sleep

class Command(BaseCommand):
    help = "Deletes the mb_dev database if it exists and appends SQL files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes", action="store_true", help="Delete the database without confirmation"
        )

    def handle(self, *args, **options):
        alias_db = "mb_devv"
        db_name = "mb_dev"

        

        confirmation = options.get("yes")
        print("Creating database")
        self.create_database(alias_db)
        try:
            if confirmation or self.confirm_action(alias_db):
                #self.drop_database(db_name)
                #self.create_database(db_name)
                self.drop_database(alias_db)
                print("Dropped database")
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully deleted and recreated 'mb_dev' database.")
                )
            else:
                self.stdout.write(self.style.WARNING(f"Operation canceled."))
        except OperationalError:
            self.stdout.write(
                self.style.WARNING(f"Database '{db_name}' does not exist. Skipping deletion.")
            )
        self.import_sql_files(db_name)

    def confirm_action(self, db_name):
        if os.isatty(0):  # Check if stdin is connected to a terminal
            db_name = db_name
            return "yes"
        

    def create_database(self, db_name):
        try:
            with connection.cursor() as cursor:
                print("Trying to create database")
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
        except Exception as e:
            print(f"An error occurred: {e}")

    def drop_database(self, db_name):
        with connection.cursor() as cursor:
            print("Destroying database")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")  # Disable foreign key checks
            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")  # Re-enable foreign key checks

    def import_sql_files(self, db_name):
        command_dir = os.path.dirname(os.path.realpath(__file__))
        sql_dir = os.path.join(command_dir, '..', 'SQL_files')
        sql_files = [f for f in os.listdir(sql_dir) if f.endswith('.sql') or f.endswith('.sql.zip')]

        for sql_file in sql_files:
            sql_file_path = os.path.join(sql_dir, sql_file)
            if os.path.exists(sql_file_path):
                try:
                    with open(sql_file_path, 'r', encoding='utf-8-sig') as f:
                        sql_query = f.read()
                except UnicodeDecodeError:
                    self.stdout.write(self.style.ERROR(f"Failed to decode SQL file: {sql_file}. Skipping..."))
                    continue
                if not self.execute_sql_query(db_name, sql_query):
                    self.stdout.write(self.style.ERROR(f"Failed to import SQL file: {sql_file}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Imported SQL file: {sql_file} into '{db_name}' database"))
            else:
                self.stdout.write(self.style.WARNING(f"SQL file not found: {sql_file}"))

    def execute_sql_query(self, db_name, sql_query):
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
            return True
        except OperationalError as e:
            print(f"OperationalError: {e}. Attempting to reconnect to the database...")
            # Attempt to reconnect to the database
            for _ in range(3):  # Try reconnecting 3 times
                try:
                    connection.connect()
                    print("Reconnected to the database.")
                    # Retry the SQL query
                    with connection.cursor() as cursor:
                        cursor.execute(sql_query)
                    return True
                except OperationalError:
                    print("Reconnection failed. Retrying...")
                    sleep(1)  # Wait for a short period before retrying
            print("Failed to reconnect to the database after multiple attempts.")
            return False