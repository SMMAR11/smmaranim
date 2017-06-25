# coding: utf-8

# Import
from app.decorators import *

'''
Affichage du menu de gestion des animations
_req : Objet requête
'''
@can_access('gest_anim')
def ger_anim(_req) :

	# Imports
	from app.forms.gest_anim import FiltrerAnimation
	from app.functions.form_init import sub as form_init
	from app.models import TUtilisateur
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	# Obtention d'une instance TUtilisateur
	obj_util_connect = TUtilisateur.get_util_connect(_req)

	if _req.method == 'GET' :

		# Initialisation du formulaire
		form_filtr_anim = FiltrerAnimation(kw_util = obj_util_connect)

		# Affichage du template
		output = render(_req, './gest_anim/ger_anim.html', {
			'cal_filtr_anim' : form_filtr_anim.get_calendar(_req),
			'form_filtr_anim' : form_init(form_filtr_anim),
			'title' : 'Gestion des animations'
		})

	else :
		if 'action' in _req.GET :

			# Réinitialisation du calendrier des animations
			if _req.GET['action'] == 'filtrer-animations' :

				# Soumission du formulaire
				form_filtr_anim = FiltrerAnimation(_req.POST, kw_util = obj_util_connect)

				# Mise à jour du calendrier ou affichage des erreurs
				if form_filtr_anim.is_valid() :
					output = HttpResponse(
						json.dumps({ 'success' : {
							'elements' : [['#za_cal_anim', form_filtr_anim.get_calendar(_req)]] }
						}),
						content_type = 'application/json'
					)
				else :
					output = HttpResponse(json.dumps(form_filtr_anim.errors), content_type = 'application/json')

	return output