# Generated by Django 4.1 on 2022-08-24 04:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_ingredient_measurement_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1, message='Должно быть больше 1')], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Выберите Теги', related_name='recipes_tag', to='app.tag', verbose_name='Тег'),
        ),
    ]
