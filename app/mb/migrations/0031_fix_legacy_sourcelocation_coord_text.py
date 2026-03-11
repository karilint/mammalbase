from django.db import migrations


def noop(apps, schema_editor):
    """
    Intentionally left as no-op.

    `coord_text` schema drift was found on
    `recode_extraction_extractedassertionmodel` (handled by
    `recode_extraction.0008_fix_legacy_extractedassertion_coord_text`), not on
    `mb_sourcelocation`.
    """
    return


def noop_reverse(apps, schema_editor):
    # Legacy cleanup only; no reverse operation required.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('mb', '0030_alter_attributegrouprelation_created_by_and_more'),
    ]

    operations = [
        migrations.RunPython(noop, noop_reverse),
    ]
