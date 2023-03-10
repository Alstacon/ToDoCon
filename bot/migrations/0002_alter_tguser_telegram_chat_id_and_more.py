# Generated by Django 4.1.4 on 2023-02-02 20:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tguser',
            name='telegram_chat_id',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='tguser',
            name='telegram_user_id',
            field=models.CharField(blank=True, default=None, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='tguser',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='tguser',
            name='verification_code',
            field=models.CharField(blank=True, default=None, max_length=80, null=True),
        ),
    ]
