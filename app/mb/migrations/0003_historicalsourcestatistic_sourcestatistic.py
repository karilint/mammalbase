# Generated by Django 3.2.12 on 2022-06-14 12:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
#import django_userforeignkey.models.fields
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mb', '0002_auto_20220614_1503'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalSourceStatistic',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('modified_on', models.DateTimeField(blank=True, editable=False)),
                ('history_change_reason', models.TextField(null=True)),
                ('is_active', models.BooleanField(default=True, help_text='Is the record active')),
                ('name', models.CharField(help_text='Enter the statistic described in the Reference', max_length=500)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('created_by', models.ForeignKey(blank=True, db_constraint=False, editable=False, null=True, on_delete=models.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='The user that is automatically assigned')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, db_constraint=False, editable=False, null=True, on_delete=models.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='The user that is automatically assigned')),
                ('reference', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='mb.sourcereference')),
            ],
            options={
                'verbose_name': 'historical source statistic',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='SourceStatistic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True, help_text='Is the record active')),
                ('name', models.CharField(help_text='Enter the statistic described in the Reference', max_length=500)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=models.SET_NULL, related_name='createdby_sourcestatistic', to=settings.AUTH_USER_MODEL, verbose_name='The user that is automatically assigned')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=models.SET_NULL, related_name='modifiedby_sourcestatistic', to=settings.AUTH_USER_MODEL, verbose_name='The user that is automatically assigned')),
                ('reference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mb.sourcereference')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('reference', 'name')},
            },
        ),
    ]
