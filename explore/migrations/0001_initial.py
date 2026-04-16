from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Species",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                (
                    "category",
                    models.CharField(
                        choices=[("bird", "Bird"), ("insect", "Insect"), ("mammal", "Mammal")],
                        max_length=20,
                    ),
                ),
                ("habitat", models.CharField(max_length=120)),
                ("summary", models.TextField()),
                ("image_url", models.URLField(blank=True)),
            ],
            options={
                "verbose_name_plural": "species",
                "ordering": ["category", "name"],
            },
        ),
    ]
