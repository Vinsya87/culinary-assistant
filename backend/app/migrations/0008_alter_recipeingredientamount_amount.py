# Generated by Django 4.1 on 2022-08-24 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_recipe_cooking_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredientamount',
            name='amount',
            field=models.PositiveSmallIntegerField(verbose_name='Количество ингредиента'),
        ),
    ]
