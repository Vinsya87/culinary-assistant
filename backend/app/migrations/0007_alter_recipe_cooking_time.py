# Generated by Django 4.1 on 2022-08-24 04:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_recipe_cooking_time_alter_recipe_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1, message='Должно быть больше 1')], verbose_name='Время приготовления'),
        ),
    ]
