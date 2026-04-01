from django.db import migrations


MODEL_COLUMNS = {
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

# Known legacy drift columns observed in older deployments.
KNOWN_LEGACY_COLUMNS = {
    'snippet',
    'coord_text',
    'count_text',
    'sex_text',
    'date_text',
}


def drop_legacy_columns(apps, schema_editor):
    """
    Older DBs can retain obsolete columns on
    recode_extraction_extractedassertionmodel (e.g. snippet/count_text).
    Those may be NOT NULL without defaults and break INSERTs.
    """
    connection = schema_editor.connection
    table_name = 'recode_extraction_extractedassertionmodel'

    with connection.cursor() as cursor:
        if table_name not in connection.introspection.table_names(cursor):
            return

        description = connection.introspection.get_table_description(cursor, table_name)
        existing = {col.name for col in description}

        # Drop explicitly known drift columns and any unexpected *_text leftovers.
        drift = {
            name for name in existing
            if name in KNOWN_LEGACY_COLUMNS
            or (name.endswith('_text') and name not in MODEL_COLUMNS)
        }
        if not drift:
            return

        qn = schema_editor.quote_name
        for column in sorted(drift):
            cursor.execute(f"ALTER TABLE {qn(table_name)} DROP COLUMN {qn(column)}")


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('recode_extraction', '0010_drop_remaining_legacy_extractedassertion_text_columns'),
    ]

    operations = [
        migrations.RunPython(drop_legacy_columns, noop_reverse),
    ]
