from django.db import migrations


LEGACY_COLUMNS = (
    'coord_text',
    'count_text',
    'sex_text',
)


def drop_legacy_text_columns_if_present(apps, schema_editor):
    """
    Older deployments may contain legacy *_text columns on
    recode_extraction_extractedassertionmodel that are not part of the current
    Django model. If these legacy columns are NOT NULL without defaults,
    assertion INSERTs fail with MySQL 1364 errors.
    """
    connection = schema_editor.connection
    table_name = 'recode_extraction_extractedassertionmodel'

    with connection.cursor() as cursor:
        table_names = connection.introspection.table_names(cursor)
        if table_name not in table_names:
            return

        description = connection.introspection.get_table_description(cursor, table_name)
        column_names = {col.name for col in description}

        qn = schema_editor.quote_name
        for column in LEGACY_COLUMNS:
            if column in column_names:
                cursor.execute(f"ALTER TABLE {qn(table_name)} DROP COLUMN {qn(column)}")


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('recode_extraction', '0008_fix_legacy_extractedassertion_coord_text'),
    ]

    operations = [
        migrations.RunPython(drop_legacy_text_columns_if_present, noop_reverse),
    ]
