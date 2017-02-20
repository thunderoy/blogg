from django.db import models

from taggit.managers import TaggableManager

class Blog(models.Model):
	title = models.CharField(max_length=100)
	content = models.TextField()
	tags = TaggableManager()
	comments = models.TextField()
	status = models.CharField(max_length=10)

	def __str__(self):
		return self.title