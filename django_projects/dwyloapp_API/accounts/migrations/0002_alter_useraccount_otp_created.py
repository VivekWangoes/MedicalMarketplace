# Generated by Django 3.2 on 2022-02-22 06:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='otp_created',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 2, 22, 6, 24, 59, 561585), null=True),
        ),
    ]
