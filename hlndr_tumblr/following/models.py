from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Following(models.Model):
	
	def __unicode__(self):
		return self.user.username
	
