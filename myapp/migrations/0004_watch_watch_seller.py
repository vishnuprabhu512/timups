# Generated by Django 3.0 on 2021-11-19 05:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_watch'),
    ]

    operations = [
        migrations.AddField(
            model_name='watch',
            name='watch_seller',
            field=models.ForeignKey(default='2', on_delete=django.db.models.deletion.CASCADE, to='myapp.User'),
        ),
    ]