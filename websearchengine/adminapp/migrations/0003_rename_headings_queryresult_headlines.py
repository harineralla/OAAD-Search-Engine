# Generated by Django 4.2.2 on 2023-07-12 23:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0002_remove_queryresult_result_queryresult_headings_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='queryresult',
            old_name='headings',
            new_name='headlines',
        ),
    ]
