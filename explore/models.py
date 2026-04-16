from django.db import models
from django.urls import reverse


class Species(models.Model):
    CATEGORY_CHOICES = [
        ("bird", "Bird"),
        ("insect", "Insect"),
        ("mammal", "Mammal"),
    ]

    name = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    habitat = models.CharField(max_length=120)
    summary = models.TextField()
    image_url = models.URLField(blank=True)

    class Meta:
        ordering = ["category", "name"]
        verbose_name_plural = "species"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("species_detail", args=[self.pk])
