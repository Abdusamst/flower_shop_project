# Generated by Django 4.2.17 on 2025-02-09 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_delete_poster'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=20, verbose_name='Новая цена'),
        ),
    ]
