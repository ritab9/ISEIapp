# Generated by Django 3.2.6 on 2024-05-08 15:21

from django.db import migrations, models
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0087_rename_tn_county_tncounty'),
        ('reporting', '0024_annualreport_last_update_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='TN_county',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.tncounty'),
        ),
        migrations.AlterField(
            model_name='student',
            name='address',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='student',
            name='age_at_registration',
            field=models.PositiveIntegerField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='annual_report',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='students', to='reporting.annualreport'),
        ),
        migrations.AlterField(
            model_name='student',
            name='baptized',
            field=models.BooleanField(default='', null=True),
        ),
        migrations.AlterField(
            model_name='student',
            name='birth_date',
            field=models.DateField(default=''),
        ),
        migrations.AlterField(
            model_name='student',
            name='country',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, to='users.country'),
        ),
        migrations.AlterField(
            model_name='student',
            name='grade_level',
            field=models.CharField(choices=[('K', 'K'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12')], default='', max_length=2),
        ),
        migrations.AlterField(
            model_name='student',
            name='is_at_least_one_parent_sda',
            field=models.BooleanField(default='', null=True, verbose_name='Parent SDA'),
        ),
        migrations.AlterField(
            model_name='student',
            name='location',
            field=models.CharField(choices=[('on-site', 'On-Site'), ('satelite', 'Satelite'), ('distance-learning', 'Distance-Learning')], default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='student',
            name='name',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='student',
            name='registration_date',
            field=models.DateField(default=''),
        ),
        migrations.AlterField(
            model_name='student',
            name='status',
            field=models.CharField(choices=[('enrolled', 'Enrolled'), ('graduated', 'Graduated Last Year'), ('did_not_return', 'Did Not Return')], default='', max_length=15),
        ),
        migrations.AlterField(
            model_name='student',
            name='us_state',
            field=users.models.StateField(blank=True, choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming')], default='', max_length=2, null=True, verbose_name='US State'),
        ),
        migrations.AlterField(
            model_name='student',
            name='withdraw_date',
            field=models.DateField(blank=True, default='', null=True),
        ),
    ]
