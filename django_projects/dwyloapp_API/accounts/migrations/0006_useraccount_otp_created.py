# Generated by Django 3.2 on 2022-02-11 10:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_contactsupport'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='otp_created',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 2, 11, 10, 56, 57, 859463), null=True),
        ),
    ]
