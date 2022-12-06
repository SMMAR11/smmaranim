# coding: utf-8

# Imports
from app.models import *
from django.db import models

class PrestatairesMarcheManager(models.Manager):
	
	def get_lots(self, oOrg):
		from django.db.models import Q
		return self.filter(Q(id_prest=oOrg.pk) | Q(id_prest2=oOrg.pk))