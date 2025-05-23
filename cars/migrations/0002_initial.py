# Generated by Django 5.0.1 on 2025-05-10 18:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("cars", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bookings",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Foydalanuvchi",
            ),
        ),
        migrations.AddField(
            model_name="car",
            name="brand",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cars",
                to="cars.brand",
                verbose_name="Brend",
            ),
        ),
        migrations.AddField(
            model_name="booking",
            name="car",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bookings",
                to="cars.car",
                verbose_name="Avtomobil",
            ),
        ),
        migrations.AddField(
            model_name="contract",
            name="booking",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="contract",
                to="cars.booking",
                verbose_name="Buyurtma",
            ),
        ),
        migrations.AddField(
            model_name="contract",
            name="car",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="contracts",
                to="cars.car",
                verbose_name="Avtomobil",
            ),
        ),
        migrations.AddField(
            model_name="contract",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="contracts",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Foydalanuvchi",
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="booking",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment",
                to="cars.booking",
                verbose_name="Buyurtma",
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payments",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Foydalanuvchi",
            ),
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(
                fields=["status", "created_at"], name="cars_bookin_status_a56127_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(
                fields=["user", "status"], name="cars_bookin_user_id_2e2c22_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(
                fields=["status", "created_at"], name="cars_paymen_status_b3d3dc_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(
                fields=["user", "status"], name="cars_paymen_user_id_e63ff9_idx"
            ),
        ),
    ]
