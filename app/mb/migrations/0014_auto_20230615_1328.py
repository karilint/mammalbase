# Generated by Django 3.2.19 on 2023-06-15 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mb', '0013_merge_0012_auto_20230523_1304_0012_auto_20230602_2148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalmasterreference',
            name='citation',
            field=models.CharField(help_text='Enter the Citation of the Standard Reference', max_length=500),
        ),
        migrations.AlterField(
            model_name='masterreference',
            name='citation',
            field=models.CharField(help_text='Enter the Citation of the Standard Reference', max_length=500),
        ),
    ]
