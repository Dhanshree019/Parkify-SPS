# Generated by Django 4.1.2 on 2022-10-05 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='images',
            name='license_no',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
    ]
