# Generated by Django 2.1 on 2019-04-07 10:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('rebook', '0009_ratings_numberstars'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ratings',
            name='id',
        ),
        migrations.AddField(
            model_name='proposal',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ratings',
            name='numberStars',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
