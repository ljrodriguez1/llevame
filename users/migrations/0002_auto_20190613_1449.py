# Generated by Django 2.2.1 on 2019-06-13 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='ida',
            field=models.CharField(default='None', max_length=50),
        ),
    ]