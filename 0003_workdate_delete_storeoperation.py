# Generated by Django 5.1.1 on 2024-09-16 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_storeoperation'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkDate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
            ],
        ),
        migrations.DeleteModel(
            name='StoreOperation',
        ),
    ]