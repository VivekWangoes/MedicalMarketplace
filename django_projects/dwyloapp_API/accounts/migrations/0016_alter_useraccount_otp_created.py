# Generated by Django 3.2 on 2022-02-16 13:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_alter_useraccount_otp_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='otp_created',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 2, 16, 13, 19, 0, 300152), null=True),
        ),
    ]
