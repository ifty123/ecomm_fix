# Generated by Django 4.2 on 2023-04-12 03:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toko', '0005_rename_produkitem_orderprodukitem_produk_item'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='produkItems',
            new_name='produk_items',
        ),
    ]
