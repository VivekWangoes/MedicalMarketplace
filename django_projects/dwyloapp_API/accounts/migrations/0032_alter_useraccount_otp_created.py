# Generated by Django 3.2 on 2022-02-18 12:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0031_alter_useraccount_otp_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='otp_created',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 2, 18, 12, 46, 23, 40640), null=True),
        ),
    ]
