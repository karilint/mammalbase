from django.db import migrations


class Migration(migrations.Migration):
    """
    Historical migration.

    This migration originally added `provider_id` to
    socialaccount_socialapp before django-allauth shipped
    its own migration.

    django-allauth >= 0.55 includes
    socialaccount.0004_app_provider_id_settings, so this
    migration must now be a NO-OP to avoid duplicate columns.
    """

    initial = True

    dependencies = [
        ("socialaccount", "0003_extra_data_default_dict"),
    ]

    operations = [
        migrations.RunPython(
            migrations.RunPython.noop,
            migrations.RunPython.noop,
        ),
    ]
