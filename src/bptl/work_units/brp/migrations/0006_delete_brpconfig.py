# Generated by Django 2.2.14 on 2020-11-16 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("brp", "0005_move_brp_config_to_default_service"),
    ]

    operations = [
        migrations.DeleteModel(
            name="BRPConfig",
        ),
    ]
