from django.db import migrations


def drop_legacy_coord_text_if_present(apps, schema_editor):
    """
    Older deployments may still have a legacy coord_text column on mb_sourcelocation
    that is NOT NULL and has no default. The current SourceLocation model does not
    define this column, so INSERTs that only set locality fields can fail.
    """
    connection = schema_editor.connection
    table_name = 'mb_sourcelocation'

    with connection.cursor() as cursor:
        table_names = connection.introspection.table_names(cursor)
        if table_name not in table_names:
            return

        description = connection.introspection.get_table_description(cursor, table_name)
        column_names = {col.name for col in description}
        if 'coord_text' not in column_names:
            return

        qn = schema_editor.quote_name
        cursor.execute(f"ALTER TABLE {qn(table_name)} DROP COLUMN {qn('coord_text')}")


def noop_reverse(apps, schema_editor):
    # Legacy cleanup only; no reverse operation required.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('mb', '0030_alter_attributegrouprelation_created_by_and_more'),
    ]

    operations = [
        migrations.RunPython(drop_legacy_coord_text_if_present, noop_reverse),
    ]
