from django.db import models

# Create your models here.

class Users(models.Model):
	usuario = models.CharField(max_length=20)
	password = models.CharField(max_length=50)
	id_fb = models.IntegerField(max_length=100)
	acces_token = models.CharField(max_length=500)
	def __unicode__(self):
		return self.usuario

class Friends(models.Model):
	id_fb = models.IntegerField(max_length=100)
	name = models.CharField(max_length=100)
	date = models.CharField(max_length=12)
	photo = models.CharField(max_length=500)
	def __unicode__(self):
		return self.name



