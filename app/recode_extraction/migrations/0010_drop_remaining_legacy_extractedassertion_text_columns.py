from django.db import migrations


ALLOWED_COLUMNS = {
    'id',
    'extraction_run_id',
    'subject_taxon',
    'trait_name',
    'value_raw',
    'unit',
    'context',
    'confidence',
    'evidence_start',
    'evidence_end',
    'page_number',
    'mapped_trait_id',
    'ets_payload',
    'ets_persisted',
    'review_status',
    'edited_value',
    'edited_unit',
    'reviewer_note',
    'reviewed_by_id',
    'reviewed_at',
    'unmapped_reason',
    'qc_errors',
    'created_at',
}


def drop_remaining_legacy_text_columns(apps, schema_editor):
    """
    Remove any leftover legacy *_text columns on
    recode_extraction_extractedassertionmodel that are not represented by the
    current Django model. Some old deployments still have columns like
    date_text/count_text/sex_text that can be NOT NULL without defaults.
    """
    connection = schema_editor.connection
    table_name = 'recode_extraction_extractedassertionmodel'

    with connection.cursor() as cursor:
        table_names = connection.introspection.table_names(cursor)
        if table_name not in table_names:
            return

        description = connection.introspection.get_table_description(cursor, table_name)
        column_names = {col.name for col in description}

        to_drop = sorted(
            name for name in column_names
            if name.endswith('_text') and name not in ALLOWED_COLUMNS
        )
        if not to_drop:
            return

        qn = schema_editor.quote_name
        for column in to_drop:
            cursor.execute(f"ALTER TABLE {qn(table_name)} DROP COLUMN {qn(column)}")


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('recode_extraction', '0009_drop_legacy_extractedassertion_text_columns'),
    ]

    operations = [
        migrations.RunPython(drop_remaining_legacy_text_columns, noop_reverse),
    ]
