# coding: utf-8

'''
Affichage de la page principale ou traitement d'une requête quelconque
_req : Objet requête
'''
def index(_req) :

	# Imports
	from app.apps import AppConfig
	from app.forms.index import Authentifier
	from app.functions.form_init import sub as form_init
	from app.functions.menu_init import sub as menu_init
	from app.functions.modal_init import sub as modal_init
	from app.models import TUtilisateur
	from django.contrib.auth import authenticate
	from django.contrib.auth import login
	from django.contrib.auth import logout
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	# Tentative d'obtention d'une instance TUtilisateur
	obj_util_connect = TUtilisateur.get_util_connect(_req)

	if _req.method == 'GET' :
		if 'action' in _req.GET :

			# Déconnexion de la plateforme
			if _req.GET['action'] == 'logout' :

				# Nettoyage des variables de session
				for cle in list(_req.session.keys()) : del _req.session[cle]

				# Désactivation du mode super-administrateur
				if obj_util_connect and obj_util_connect.get_en_mode_superadmin() == True :
					obj_util_connect.en_mode_superadmin = False; obj_util_connect.save()

				# Fermeture de la session
				logout(_req)

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'Merci pour votre connexion sur la plateforme {}.'.format(AppConfig.verbose_name),
						'redirect' : reverse('index')
					}}),
					content_type = 'application/json'
				)

			# Activation du mode super-administrateur
			if _req.GET['action'] == 'activer-mode-super-administrateur' :
				if obj_util_connect and obj_util_connect.get_est_superadmin() == 0 :

					# Mise à jour de l'instance
					obj_util_connect.en_mode_superadmin = True; obj_util_connect.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : 'Vous venez d\'activer le mode super-administrateur.',
							'redirect' : '__RELOAD__'
						}}),
						content_type = 'application/json'
					)

			# Désactivation du mode super-administrateur
			if _req.GET['action'] == 'desactiver-mode-super-administrateur' :
				if obj_util_connect and obj_util_connect.get_est_superadmin() == 1 :

					# Mise à jour de l'instance
					obj_util_connect.en_mode_superadmin = False; obj_util_connect.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : 'Vous venez de désactiver le mode super-administrateur.',
							'redirect' : '__RELOAD__'
						}}),
						content_type = 'application/json'
					)

		else :

			# Initialisation du formulaire
			form_auth = Authentifier()

			# Déclaration des fenêtres modales
			modals = [modal_init('login', 'Connexion à la plateforme {}'.format(AppConfig.verbose_name))]

			# Affichage du template
			output = render(_req, './index.html', {
				'form_auth' : form_init(form_auth),
				'menu' : menu_init(_req, '__ALL__', 3),
				'modals' : modals,
				'title' : 'Accueil' if _req.user.is_authenticated() else 'Identification'
			})

	else :

		# Connexion à la plateforme
		if 'action' in _req.GET and _req.GET['action'] == 'login' :

			# Soumission du formulaire
			form_auth = Authentifier(_req.POST)

			if form_auth.is_valid() :

				# Stockage des données du formulaire
				cleaned_data = form_auth.cleaned_data
				val_username = cleaned_data.get('zs_username')
				val_password = cleaned_data.get('zs_password')

				# Déclaration de la session
				login(_req, authenticate(username = val_username, password = val_password))

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'Bienvenue sur la plateforme {}.'.format(AppConfig.verbose_name),
						'redirect' : '__RELOAD__'
					}}),
					content_type = 'application/json'
				)

			else :

				# Affichage des erreurs
				output = HttpResponse(json.dumps(form_auth.errors), content_type = 'application/json')

	return output