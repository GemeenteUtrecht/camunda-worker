# Generated by Django 2.2.10 on 2020-02-26 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("activiti", "0007_copy_tasks_to_parent"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="servicetask",
            name="execution_error",
        ),
        migrations.RemoveField(
            model_name="servicetask",
            name="id",
        ),
        migrations.RemoveField(
            model_name="servicetask",
            name="result_variables",
        ),
        migrations.RemoveField(
            model_name="servicetask",
            name="status",
        ),
        migrations.RemoveField(
            model_name="servicetask",
            name="topic_name",
        ),
        migrations.RemoveField(
            model_name="servicetask",
            name="variables",
        ),
    ]
