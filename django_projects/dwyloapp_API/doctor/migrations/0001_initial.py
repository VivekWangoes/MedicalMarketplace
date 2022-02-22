# Generated by Django 3.2 on 2022-02-21 12:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DoctorProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('doctor_pic', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('gender', models.CharField(blank=True, choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')], max_length=50, null=True)),
                ('career_started', models.DateField(blank=True, null=True)),
                ('specialty', models.CharField(blank=True, max_length=50, null=True)),
                ('location_city', models.CharField(blank=True, max_length=50, null=True)),
                ('clinic', models.CharField(blank=True, max_length=100, null=True)),
                ('consultation_fees', models.IntegerField(blank=True, null=True)),
                ('expertise_area', models.TextField(blank=True, null=True)),
                ('verification', models.CharField(blank=True, default='Incompleted', max_length=50, null=True)),
                ('doctor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DoctorSlots',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('slot_time', models.DateTimeField(blank=True, null=True)),
                ('is_booked', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DoctorReviews',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('review', models.TextField()),
                ('prescription_rating', models.CharField(blank=True, max_length=10, null=True)),
                ('explanation_rating', models.CharField(blank=True, max_length=10, null=True)),
                ('friendliness_rating', models.CharField(blank=True, max_length=10, null=True)),
                ('doctor_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctor.doctorprofile')),
                ('user_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DoctorAvailability',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('slot_date', models.DateField(blank=True, null=True)),
                ('day', models.CharField(blank=True, max_length=50, null=True)),
                ('slot', models.CharField(blank=True, choices=[('MORNING', 'Morning'), ('EVENING', 'EVENING')], max_length=50, null=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_availabitily', to='doctor.doctorprofile')),
                ('time_slot', models.ManyToManyField(to='doctor.DoctorSlots')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Appointments',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(blank=True, choices=[('COMPLETED', 'Completed'), ('UPCOMING', 'Upcoming'), ('CANCLE', 'Cancle')], max_length=50, null=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_appointment', to='doctor.doctorprofile')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient_appointment', to=settings.AUTH_USER_MODEL)),
                ('slot', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_slot', to='doctor.doctorslots')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]