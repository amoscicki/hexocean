# Generated by Django 4.2.6 on 2023-10-15 19:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_link_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='link',
            name='link',
        ),
    ]