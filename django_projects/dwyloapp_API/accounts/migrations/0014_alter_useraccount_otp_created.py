# Generated by Django 3.2 on 2022-02-16 09:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_alter_useraccount_otp_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='otp_created',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 2, 16, 9, 57, 41, 807117), null=True),
        ),
    ]
