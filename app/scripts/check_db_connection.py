import time

from django.db import connection
from django.db.utils import OperationalError

DB_CONN = None
for i in range(30):
    try:
        connection.ensure_connection()
        DB_CONN = True
        break
    except OperationalError:
        print(f"WAITING FOR DATABASE... ({i}s)")
        time.sleep(1)

if DB_CONN:
    print("CONNECTED TO DATABASE!")
else:
    print("DATABASE UNAVAILABLE FOR 30 SECONDS... "
          "CHECK WHETHER THE DATABASE CONTAINER IS RUNNING AND RESTART THE APP... ")
    raise OperationalError(
        "DATABASE UNAVAILABLE FOR 30 SECONDS... "
        "CHECK WHETHER THE DATABASE CONTAINER IS RUNNING AND RESTART THE APP... "
        "EXITING...")
