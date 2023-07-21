# Generated by Django 4.2.2 on 2023-07-21 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminapp', '0003_rename_headings_queryresult_headlines'),
    ]

    operations = [
        migrations.AddField(
            model_name='queryresult',
            name='access_frequency',
            field=models.PositiveIntegerField(default=8),
        ),
        migrations.AddField(
            model_name='queryresult',
            name='payment',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]