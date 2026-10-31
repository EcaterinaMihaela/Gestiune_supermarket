from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supermarket_online', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE furnizori
                ADD COLUMN tip VARCHAR(30) NOT NULL DEFAULT 'DIVERSE'
            """,
            reverse_sql="""
                ALTER TABLE furnizori
                DROP COLUMN tip
            """,
        ),
    ]