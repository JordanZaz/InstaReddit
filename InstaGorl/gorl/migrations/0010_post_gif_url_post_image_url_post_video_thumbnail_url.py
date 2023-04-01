# Generated by Django 4.1.4 on 2023-01-29 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gorl', '0009_post_gif_post_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='gif_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='video_thumbnail_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
