from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('zxui', '0002_seed_defaults'),
    ]

    operations = [
        migrations.AddField(
            model_name='commandtemplate',
            name='category',
            field=models.CharField(blank=True, default='', max_length=60),
        ),
        migrations.AddField(
            model_name='commandtemplate',
            name='tags',
            field=models.JSONField(default=list),
        ),
    ]
