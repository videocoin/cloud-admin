# Generated by Django 2.2 on 2019-12-16 08:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=255, primary_key=True, serialize=False)),
                ('email', models.EmailField(blank=True, max_length=255, null=True, unique=True)),
                ('password', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('activated_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('token', models.CharField(blank=True, max_length=255, null=True)),
                ('role', models.IntegerField(choices=[(0, 'Regular'), (3, 'QA'), (6, 'Manager'), (9, 'Super')])),
            ],
            options={
                'db_table': 'users',
                'ordering': ('-created_at',),
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ApiToken',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, max_length=36, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('token', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Token',
                'verbose_name_plural': 'Tokens',
                'db_table': 'user_api_tokens',
                'ordering': ('-created_at',),
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TestingUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delete_date', models.DateTimeField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='testing_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
