# Generated by Django 2.2.14 on 2020-12-22 16:04

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("camunda", "0013_externaltask_instance_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="externaltask",
            name="camunda_error",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True, default=None, null=True, verbose_name="camunda error"
            ),
        ),
    ]
