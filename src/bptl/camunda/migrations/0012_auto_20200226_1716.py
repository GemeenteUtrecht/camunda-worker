# Generated by Django 2.2.10 on 2020-02-26 16:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("camunda", "0011_auto_20200226_1441"),
    ]

    operations = [
        migrations.AlterField(
            model_name="externaltask",
            name="basetask_ptr",
            field=models.OneToOneField(
                auto_created=True,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="tasks.BaseTask",
            ),
        ),
    ]
