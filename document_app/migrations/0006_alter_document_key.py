# Generated by Django 4.0.1 on 2022-01-30 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_app', '0005_remove_document_id_alter_document_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='key',
            field=models.CharField(max_length=36, primary_key=True, serialize=False),
        ),
    ]
