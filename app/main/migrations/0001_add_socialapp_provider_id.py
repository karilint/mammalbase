from django.db import migrations


def _column_exists(connection, table_name, column_name):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = %s
              AND COLUMN_NAME = %s
            LIMIT 1
            """,
            [table_name, column_name],
        )
        return cursor.fetchone() is not None


def _table_exists(connection, table_name):
    return table_name in connection.introspection.table_names()


def add_provider_id(apps, schema_editor):
    if schema_editor.connection.vendor != "mysql":
        return
    table_name = "socialaccount_socialapp"
    account_table = "socialaccount_socialaccount"
    if not _table_exists(schema_editor.connection, table_name):
        return
    if _column_exists(schema_editor.connection, table_name, "provider_id"):
        provider_id_exists = True
    else:
        provider_id_exists = False
    if not provider_id_exists:
        schema_editor.execute(
            (
                "ALTER TABLE `{table}` "
                "ADD COLUMN `provider_id` varchar(200) NOT NULL DEFAULT ''"
            ).format(table=table_name)
        )
    if not _column_exists(schema_editor.connection, table_name, "settings"):
        schema_editor.execute(
            (
                "ALTER TABLE `{table}` "
                "ADD COLUMN `settings` json NULL"
            ).format(table=table_name)
        )
        schema_editor.execute(
            (
                "UPDATE `{table}` SET `settings` = '{{}}' "
                "WHERE `settings` IS NULL"
            ).format(table=table_name)
        )
        schema_editor.execute(
            (
                "ALTER TABLE `{table}` "
                "MODIFY COLUMN `settings` json NOT NULL"
            ).format(table=table_name)
        )
    if _table_exists(schema_editor.connection, account_table):
        if _column_exists(schema_editor.connection, account_table, "provider"):
            schema_editor.execute(
                (
                    "ALTER TABLE `{table}` "
                    "MODIFY COLUMN `provider` varchar(200) NOT NULL"
                ).format(table=account_table)
            )


def remove_provider_id(apps, schema_editor):
    if schema_editor.connection.vendor != "mysql":
        return
    table_name = "socialaccount_socialapp"
    if not _table_exists(schema_editor.connection, table_name):
        return
    if not _column_exists(schema_editor.connection, table_name, "provider_id"):
        return
    schema_editor.execute(
        "ALTER TABLE `{table}` DROP COLUMN `provider_id`".format(table=table_name)
    )


class Migration(migrations.Migration):
    initial = True
    atomic = False

    dependencies = [
        ("socialaccount", "0003_extra_data_default_dict"),
    ]

    operations = [
        migrations.RunPython(add_provider_id, reverse_code=remove_provider_id),
    ]
