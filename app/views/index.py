# coding: utf-8

# Import
from app.decorators import*

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

'''
Affichage de la page de consultation du compte utilisateur ou traitement d'une requête quelconque
_req : Objet requête
'''
@can_access()
def consult_compte(_req) :

	# Imports
	from app.forms.gest_marches import GererTransactionDemiJournees
	from app.forms.index import GererUtilisateur
	from app.functions.attributes_init import sub as attributes_init
	from app.functions.form_init import sub as form_init
	from app.functions.modal_init import sub as modal_init
	from app.models import TPrestatairesMarche
	from app.models import TUtilisateur
	from django.forms import formset_factory
	from django.http import HttpResponse
	from django.shortcuts import render
	from django.template.context_processors import csrf
	from functools import partial
	from functools import wraps
	import json

	output = None

	# Obtention d'une instance TUtilisateur
	obj_util_connect = TUtilisateur.get_util_connect(_req)

	if _req.method == 'GET' :
		if 'action' in _req.GET :

			# Initialisation du formset relatif aux demi-journées de préparation et de réalisation
			if _req.GET['action'] == 'initialiser-formset-transactions-demi-journees' and 'id' in _req.GET :

				# Obtention d'une instance TPrestatairesMarche
				obj_pm = TPrestatairesMarche.objects.get(pk = _req.GET['id'], id_prest = obj_util_connect.get_org())

				# Mise en session de l'identifiant du couple prestataire/marché
				_req.session['ttransactiondemijournees__id_pm__update'] = obj_pm.get_pk()

				output = GererTransactionDemiJournees(kw_pm = obj_pm).get_datatable(_req)

		else :

			# Initialisation des balises <tr/> de la datatable des marchés
			trs = []
			for pm in obj_util_connect.get_org().get_pm().all() :
				tds = [
					pm.get_marche(),
					pm.get_nbre_dj_ap_pm__str(),
					pm.get_nbre_dj_progr_pm('AP'),
					pm.get_nbre_dj_ap_rest_pm(),
					pm.get_nbre_dj_pp_pm__str(),
					pm.get_nbre_dj_progr_pm('PP'),
					pm.get_nbre_dj_prep_real_pm(True),
					pm.get_nbre_dj_prep_real_pm(False),
					pm.get_nbre_dj_pp_rest_pm(False),
					pm.get_nbre_dj_pp_rest_pm(True),
					'''
					<span action="?action=initialiser-formset-transactions-demi-journees&id={}"
					class="half-icon icon-without-text" modal-suffix="ger_tdj" onclick="ajax(event);"
					title="Gérer les demi-journées de préparation et de réalisation"></span>
					'''.format(pm.get_pk())
				]
				trs.append('<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tds])))

			# Initialisation des attributs utilisateur
			attrs_util = {
				'email' : { 'label' : 'Courriel', 'value' : obj_util_connect.get_email() },
				'nom_complet' : { 'label' : 'Nom complet', 'value' : obj_util_connect.get_nom_complet() },
				'org' : { 'label' : 'Organisme', 'value' : obj_util_connect.get_org() }
			}

			# Initialisation du formulaire
			form_modif_util = form_init(GererUtilisateur(instance = obj_util_connect))

			# Déclaration des fenêtres modales
			modals = [
				modal_init(
					'ger_tdj',
					'Gérer les demi-journées de préparation et de réalisation',
					'''
					<form action="?action=gerer-transactions-demi-journees" method="post" name="form_ger_tdj"
					onsubmit="ajax(event);">
						<input name="csrfmiddlewaretoken" type="hidden" value="{}">
						{}
						<button class="center-block custom-button main-button" type="submit">Valider</button>
					</form>
					{}
					'''.format(
						csrf(_req)['csrf_token'], *GererTransactionDemiJournees(kw_init = True).get_datatable(_req)
					)
				),
				modal_init(
					'modif_compte',
					'Modifier mon compte',
					'''
					<form action="" method="post" name="form_modif_compte" onsubmit="ajax(event);">
						<input name="csrfmiddlewaretoken" type="hidden" value="{}">
						<div class="row">
							<div class="col-sm-6">{}</div>
							<div class="col-sm-6">{}</div>
						</div>
						{}
						<button class="center-block custom-button main-button" type="submit">Valider</button>
					</form>
					'''.format(
						csrf(_req)['csrf_token'],
						form_modif_util['last_name'],
						form_modif_util['first_name'],
						form_modif_util['email']
					)
				)
			]

			# Affichage du template
			output = render(_req, './extras/consult_compte.html', {
				'attrs_util' : attributes_init(attrs_util),
				'modals' : modals,
				'tbody' : ''.join(trs),
				'title' : 'Consulter mon compte',
				'u' : obj_util_connect
			})

	else :
		if 'action' in _req.GET :

			# Gestion des demi-journées de préparation et de réalisation
			if _req.GET['action'] == 'gerer-transactions-demi-journees' :

				# Obtention d'une instance TPrestatairesMarche
				obj_pm = TPrestatairesMarche.objects.get(
					pk = _req.session.get('ttransactiondemijournees__id_pm__update')
				)

				# Soumission du formset
				_GererTransactionDemiJournees = formset_factory(
					wraps(GererTransactionDemiJournees)(partial(GererTransactionDemiJournees, kw_pm = obj_pm))
				)
				formset_ger_tdj = _GererTransactionDemiJournees(_req.POST)

				# Initialisation des erreurs
				erreurs = {}
				if not formset_ger_tdj.is_valid() :
					for form in formset_ger_tdj :
						for cle, val in form.errors.items() : erreurs['{}-{}'.format(form.prefix, cle)] = val

				if len(erreurs) == 0 :

					# Suppression de la variable de session si définie
					if 'ttransactiondemijournees__id_pm__update' in _req.session :
						del _req.session['ttransactiondemijournees__id_pm__update']

					# Suppression de toutes les instances TTransactionDemiJournees liées à une instance
					# TPrestatairesMarche
					obj_pm.get_tdj().all().delete()

					# Création d'une instance TTransactionDemiJournees
					for form in formset_ger_tdj : form.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : 'Le marché a été modifié avec succès.', 'redirect' : '__RELOAD__'
						}}),
						content_type = 'application/json'
					)

				else :

					# Affichage des erreurs
					output = HttpResponse(json.dumps(erreurs), content_type = 'application/json')

		else :

			# Soumission du formulaire
			form_modif_util = GererUtilisateur(_req.POST, instance = obj_util_connect)

			if form_modif_util.is_valid() :

				# Modification de l'instance TUtilisateur
				form_modif_util.save()

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'Le compte a été modifié avec succès.', 'redirect' : '__RELOAD__'
					}}),
					content_type = 'application/json'
				)

			else :

				# Affichage des erreurs
				output = HttpResponse(json.dumps(form_modif_util.errors), content_type = 'application/json')

	return output

'''
Affichage des alertes
_req : Objet requête
'''
@can_access()
def get_alert(_req) :

	# Import
	from django.shortcuts import render

	output = None

	if _req.method == 'GET' :

		# Affichage du template
		output = render(_req, './extras/get_alert.html', { 'title' : 'Alertes' })

	return output