# Generated by Django 4.2 on 2023-06-05 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("toko", "0010_produkitem_informasi_produk_alter_produkitem_merk"),
    ]

    operations = [
        migrations.AlterField(
            model_name="produkitem",
            name="informasi_produk",
            field=models.TextField(blank=True, max_length=200),
        ),
    ]