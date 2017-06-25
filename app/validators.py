# coding: utf-8

'''
Validation d'un nombre décimal relatif à un nombre de demi-journées
_val : Nombre décimal
Retourne un nombre décimal
'''
def valid_dj(_val) :

	# Import
	from django.core.exceptions import ValidationError

	if _val % 1 not in [0, 0.5] : raise ValidationError(None, code = 'invalid')

	return _val

'''
Validation d'un fichier en termes de taille
_val : Fichier uploadé
Retourne le fichier uploadé
'''
def valid_fich(_val) :

	# Imports
	from django.core.exceptions import ValidationError
	from smmaranim.custom_settings import MAX_SIZE

	if _val.size > MAX_SIZE * 1048576 :
		raise ValidationError(
			'Veuillez renseigner un fichier dont la taille est inférieure ou égale à {} Mo.'.format(MAX_SIZE)
		)

	return _val

'''
Validation d'un fichier au format PDF
_val : Fichier uploadé
Retourne le fichier uploadé
'''
def valid_pdf(_val) :

	# Imports
	import os
	from django.core.exceptions import ValidationError

	if os.path.splitext(_val.name)[1] != '.pdf' :
		raise ValidationError('Veuillez renseigner un fichier au format PDF.')

	return _val