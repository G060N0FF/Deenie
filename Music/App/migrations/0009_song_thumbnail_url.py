# Generated by Django 3.0.4 on 2020-03-24 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0008_remove_song_thumbnail_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='thumbnail_url',
            field=models.CharField(default=0, max_length=500),
            preserve_default=False,
        ),
    ]