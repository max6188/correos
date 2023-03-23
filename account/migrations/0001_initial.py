# Generated by Django 4.1.7 on 2023-02-19 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('email', models.CharField(max_length=100, unique=True)),
                ('phone_number', models.CharField(max_length=50)),
                ('address', models.TextField(blank=True, max_length=250)),
                ('note', models.TextField(blank=True, max_length=250)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
