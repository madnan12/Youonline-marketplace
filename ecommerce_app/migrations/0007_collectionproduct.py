# Generated by Django 3.2.6 on 2022-07-15 12:41

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_app', '0006_archivedproduct'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionProduct',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(blank=True, default='', max_length=32, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='collectionproduct_owner', to='ecommerce_app.businessowner')),
                ('product', models.ManyToManyField(blank=True, related_name='collectionproduct_product', to='ecommerce_app.Product')),
            ],
        ),
    ]