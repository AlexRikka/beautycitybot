# Generated by Django 4.2.9 on 2024-01-28 20:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('saloons', '0003_alter_sign_master'),
    ]

    operations = [
        migrations.AddField(
            model_name='sign',
            name='service',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='signs', to='saloons.service'),
            preserve_default=False,
        ),
    ]
