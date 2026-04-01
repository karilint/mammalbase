from django.db import migrations


def drop_legacy_coord_text_if_present(apps, schema_editor):
    """
    Older deployments may have a legacy coord_text column on
    recode_extraction_extractedassertionmodel. The current model does not define
    this column; if it is NOT NULL without default, INSERTs fail.
    """
    connection = schema_editor.connection
    table_name = 'recode_extraction_extractedassertionmodel'

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
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('recode_extraction', '0007_backfill_missing_review_columns'),
    ]

    operations = [
        migrations.RunPython(drop_legacy_coord_text_if_present, noop_reverse),
    ]
