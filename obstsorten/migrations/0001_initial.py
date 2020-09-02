# Generated by Django 3.0.7 on 2020-09-01 15:13

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ObstSorten',
            fields=[
                ('sorten_id', models.IntegerField(primary_key=True, serialize=False)),
                ('obst_type', models.IntegerField()),
                ('obst_sorte', models.CharField(help_text='Obstsorte: Name der Obstsorte. z.B. rheinischer Winterrambour', max_length=64, null=True)),
                ('pflueck_reif', models.CharField(blank=True, max_length=1024, null=True)),
                ('genuss_reif', models.CharField(blank=True, max_length=1024, null=True)),
                ('verwendung', models.CharField(max_length=1024, null=True)),
                ('geschmack', models.CharField(max_length=1024, null=True)),
                ('lagerfaehigkeit', models.CharField(max_length=1024, null=True)),
                ('alergie_info', models.CharField(max_length=1024, null=True)),
                ('www', django.contrib.postgres.fields.ArrayField(base_field=models.URLField(blank=True, max_length=256), null=True, size=5)),
            ],
        ),
        migrations.CreateModel(
            name='Wiese',
            fields=[
                ('wiesen_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('obstwiese', models.BooleanField(default=True)),
                ('bluehwiese', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ObstBaum',
            fields=[
                ('baum_id', models.AutoField(primary_key=True, serialize=False)),
                ('zustand', models.CharField(blank=True, max_length=248)),
                ('letzter_schnitt', models.DateField(blank=True, null=True)),
                ('sorten_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='obstsorten.ObstSorten')),
                ('wiese', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='obstsorten.Wiese')),
            ],
        ),
    ]
