# Generated by Django 2.0.5 on 2018-07-07 11:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schema', '0007_auto_20180707_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teaches',
            name='subject_code',
            field=models.ForeignKey(db_column='subject_code', on_delete=django.db.models.deletion.CASCADE, to='schema.subject'),
        ),
    ]
