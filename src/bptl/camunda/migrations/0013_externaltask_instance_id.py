# Generated by Django 2.2.14 on 2020-08-21 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("camunda", "0012_auto_20200226_1716"),
    ]

    operations = [
        migrations.AddField(
            model_name="externaltask",
            name="instance_id",
            field=models.CharField(default="", max_length=50, verbose_name="task id"),
            preserve_default=False,
        ),
    ]