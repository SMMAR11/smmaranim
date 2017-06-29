# coding: utf-8

'''
Mise en forme d'un objet datetime, date ou time au format local
_obj : Objet
Retourne une chaîne de caractères
'''
def sub(_obj) :

	# Imports
	from django.conf import settings
	from django.utils.formats import date_format
	from django.utils.formats import time_format
	import datetime

	output = None

	if _obj and settings.USE_L10N == True :
		if isinstance(_obj, datetime.datetime) :
			output = date_format(_obj, 'd/m/Y H:i')
		elif isinstance(_obj, datetime.date) :
			output = date_format(_obj, 'd/m/Y')
		elif isinstance(_obj, datetime.time) :
			output = time_format(_obj, 'H:i')

	return output