# Generated by Django 2.2.1 on 2019-05-24 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auto',
            name='capacity',
            field=models.IntegerField(default=4),
        ),
    ]
