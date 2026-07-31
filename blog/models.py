from django.db import models
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.CharField(max_length=100, default="UG Legon Poultry Team")
    summary = models.TextField(max_length=300, help_text="Short preview snippet for card display")
    content = models.TextField()
    cover_image_url = models.URLField(blank=True, null=True, help_text="Image link or Unsplash URL")
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})