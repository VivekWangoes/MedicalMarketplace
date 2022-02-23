# Generated by Django 3.2 on 2022-02-23 05:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('doctor', '0007_rename_doctorreviews_doctorreview'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(blank=True, choices=[('COMPLETED', 'Completed'), ('UPCOMING', 'Upcoming'), ('CANCLE', 'Cancle')], max_length=50, null=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_appointments', to='doctor.doctorprofile')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient_appointments', to=settings.AUTH_USER_MODEL)),
                ('slot', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_slot', to='doctor.doctorslot')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='Appointments',
        ),
    ]
