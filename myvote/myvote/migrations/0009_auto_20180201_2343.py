# Generated by Django 2.0.1 on 2018-02-01 23:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myvote', '0008_poll_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='myvote.Poll'),
        ),
    ]
