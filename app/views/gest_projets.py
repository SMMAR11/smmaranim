# coding: utf-8

# Import
from app.decorators import *

'''
Affichage du menu de gestion des projets
_req : Objet requête
'''
@can_access('gest_projets')
def get_menu(_req) :

	# Imports
	from app.functions.menu_init import sub as menu_init
	from django.shortcuts import render

	output = None

	if _req.method == 'GET' :

		# Affichage du template
		output = render(_req, './menu.html', {
			'menu' : menu_init(_req, 'gest_projets', 2),
			'title' : 'Gestion des projets'
		})

	return output

'''
Affichage du formulaire de gestion d'un projet ou traitement d'une requête quelconque
_req : Objet requête
_inst : Ajout ou modification ?
'''
@can_access('gest_projets')
def ger_projet(_req, _inst) :

	# Imports
	from app.forms.gest_projets import GererProjet
	from app.functions.form_init import sub as form_init
	from app.functions.modal_init import sub as modal_init
	from app.models import TProjet
	from app.models import TUtilisateur
	from django.core.urlresolvers import reverse
	from django.http import Http404
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from smmaranim.custom_settings import PKS
	import json

	output = None

	# Tentative d'obtention d'une instance TProjet (si page de modification en cours)
	if _inst == False :
		obj_projet = None
	else :
		if 'id' in _req.GET :
			obj_projet = get_object_or_404(TProjet, pk = _req.GET['id'])
		else :
			raise Http404

	# Obtention d'une instance TUtilisateur
	obj_util_connect = TUtilisateur.get_util_connect(_req)

	# Vérification du droit d'accès
	if obj_projet : obj_util_connect.can_access(obj_projet.get_org(), False)

	if _req.method == 'GET' :

		# Initialisation du formulaire
		form_ger_projet = GererProjet(instance = obj_projet, kw_util = obj_util_connect)

		# Définition du contenu de la balise <title/> (également utile à d'autres endroits)
		title = 'Modifier un projet' if obj_projet else 'Ajouter un projet'

		# Définition du message d'avertissement
		f = None
		if obj_projet :
			if obj_projet.get_type_public().get_pk() == PKS['id_type_public__jps'] :
				f = 'classes'
			elif obj_projet.get_type_public().get_pk() == PKS['id_type_public__jpes'] :
				f = 'tranches d\'âge'
		if f :
			message = '''
			Attention, si vous changez le type de public visé, alors les {} précédemment ajoutées seront supprimées.
			'''.format(f)
		else :
			message = ''

		# Affichage du template
		output = render(_req, './gest_projets/ger_projet.html', {
			'form_ger_projet' : form_init(form_ger_projet),
			'message' : message,
			'modals' : [modal_init('ger_projet', title)],
			'p' : obj_projet,
			'title' : title
		})

	else :

		# Soumission du formulaire
		form_ger_projet = GererProjet(_req.POST, instance = obj_projet, kw_util = obj_util_connect)

		if form_ger_projet.is_valid() :

			# Création/modification d'une instance TProjet
			obj_projet_valid = form_ger_projet.save()

			# Affichage du message de succès
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'Le projet a été {} avec succès.'.format('modifié' if obj_projet else 'ajouté'),
					'redirect' : reverse('consult_projet', args = [obj_projet_valid.get_pk()])
				}}),
				content_type = 'application/json'
			)

		else :

			# Affichage des erreurs
			output = HttpResponse(json.dumps(form_ger_projet.errors), content_type = 'application/json')

	return output

'''
Affichage de l'interface de choix d'un projet ou traitement d'une requête quelconque
_req : Objet requête
'''
@can_access('gest_projets')
def chois_projet(_req) :

	# Imports
	from app.forms.gest_projets import FiltrerProjet
	from app.functions.datatable_reset import sub as datatable_reset
	from app.functions.form_init import sub as form_init
	from app.models import TUtilisateur
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	if _req.method == 'GET' :

		# Initialisation du formulaire
		form_filtr_projet = FiltrerProjet(kw_org = TUtilisateur.get_util_connect(_req).get_org())

		# Affichage du template
		output = render(_req, './gest_projets/chois_projet.html', {
			'dtable_filtr_projet' : form_filtr_projet.get_datatable(_req),
			'form_filtr_projet' : form_init(form_filtr_projet),
			'title' : 'Choisir un projet'
		})

	else :

		# Soumission du formulaire
		form_filtr_projet = FiltrerProjet(_req.POST)

		# Réinitialisation de la datatable ou affichage des erreurs
		if form_filtr_projet.is_valid() :
			output = datatable_reset(form_filtr_projet.get_datatable(_req))
		else :
			output = HttpResponse(json.dumps(form_filtr_projet.errors), content_type = 'application/json')

	return output

'''
Affichage des données d'un projet ou traitement d'une requête quelconque
_req : Objet requête
_p : Instance TProjet ?
'''
@can_access('gest_projets')
def consult_projet(_req, _p) :

	# Imports
	from app.forms.gest_projets import GererClassesEcoleProjet
	from app.forms.gest_projets import GererTrancheAge
	from app.functions.modal_init import sub as modal_init
	from app.functions.yes_or_no import sub as yes_or_no
	from app.models import TProjet
	from app.models import TUtilisateur
	from django.core.urlresolvers import reverse
	from django.forms import formset_factory
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from django.template.context_processors import csrf
	from functools import partial
	from functools import wraps
	from smmaranim.custom_settings import PKS
	import json

	output = None

	# Tentative d'obtention d'une instance TProjet
	obj_projet = get_object_or_404(TProjet, pk = _p)

	# Initialisation du préfixe de chaque formulaire
	prefix_ajout_cep = 'AjouterClassesEcoleProjet'
	prefix_modif_cep = 'ModifierClassesEcoleProjet'

	# Obtention d'une instance TUtilisateur
	obj_util_connect = TUtilisateur.get_util_connect(_req)

	if _req.method == 'GET' :
		if 'action' in _req.GET :

			# Affichage d'une demande de suppression d'un projet
			if _req.GET['action'] == 'supprimer-projet-etape-1' :

				# Ajout d'une protection
				if obj_projet.get_anim().count() == 0 :
					modal_content = yes_or_no('?action=supprimer-projet-etape-2', 'suppr_projet')
				else :
					modal_content = '''
					<span class="very-important">Attention, avant de pouvoir supprimer le projet, veuillez d'abord 
					supprimer toutes les animations liées à celui-ci.</span>
					'''

				output = HttpResponse(
					json.dumps({ 'success' : { 'modal_content' : modal_content }}), content_type = 'application/json'
				)

			# Suppression d'un projet
			if _req.GET['action'] == 'supprimer-projet-etape-2' :

				# Vérification du droit d'accès
				obj_util_connect.can_access(obj_projet.get_org(), False)

				# Suppression d'une instance TProjet
				obj_projet.delete()

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'Le projet a été supprimé avec succès.',
						'redirect' : reverse('chois_projet')
					}}),
					content_type = 'application/json'
				)
 
			# Impression du projet
			if _req.GET['action'] == 'imprimer-projet' :

				# Initialisation des animations du projet
				anims = []
				for a in obj_projet.get_anim().all() :

					# Stockage des attributs du bilan
					attrs_bilan = None
					if a.get_bilan__object() :
						if a.get_bilan__object().get_ba() :
							attrs_bilan = a.get_bilan__object().get_ba().get_attrs_ba(True)
						else :
							attrs_bilan = a.get_bilan__object().get_attrs_bilan(True)

					anims.append({
						'a__object' : a,
						'a__attrs' : a.get_attrs_anim(True),
						'b__object' : a.get_bilan__object(),
						'b__attrs' : attrs_bilan
					})

				output = render(_req, './gest_projets/imprim_projet.html', {
					'anims' : anims,
					'attrs_projet' : obj_projet.get_attrs_projet(True),
					'title' : 'Imprimer un projet'
				})

		else :

			# Stockage des indicateurs d'affichage des onglets liés au jeune public
			onglets = {
				'ongl_cep' : True if obj_projet.get_type_public().get_pk() == PKS['id_type_public__jps'] else False,
				'ongl_ta' : True if obj_projet.get_type_public().get_pk() == PKS['id_type_public__jpes'] else False,
			}

			# Déclaration des fenêtres modales
			modals = [modal_init('suppr_projet', 'Êtes-vous sûr de vouloir supprimer définitivement le projet ?')]
			if onglets['ongl_cep'] == True :
				modals.append(modal_init(
					'ger_cep',
					'Gérer les classes',
					'''
					<form action="?action=gerer-classes-ecole-projet" method="post" name="form_ger_cep"
					onsubmit="ajax(event);">
						<input name="csrfmiddlewaretoken" type="hidden" value="{}">
						{}
						<button class="center-block custom-button main-button" type="submit">Valider</button>
					</form>
					{}
					'''.format(
						csrf(_req)['csrf_token'],
						*GererClassesEcoleProjet(kw_projet = obj_projet).get_datatable(_req)
					)
				))
			if onglets['ongl_ta'] == True :
				modals.append(modal_init(
					'ger_ta',
					'Gérer les tranches d\'âge',
					'''
					<form action="?action=gerer-tranche-age" method="post" name="form_ger_ta"
					onsubmit="ajax(event);">
						<input name="csrfmiddlewaretoken" type="hidden" value="{}">
						{}
						<button class="center-block custom-button main-button" type="submit">Valider</button>
					</form>
					{}
					'''.format(
						csrf(_req)['csrf_token'],
						*GererTrancheAge(kw_projet = obj_projet).get_datatable(_req)
					)
				))

			# Affichage du template
			output = render(_req, './gest_projets/consult_projet.html', {
				'attrs_projet' : obj_projet.get_attrs_projet(),
				'can_access' : obj_util_connect.can_access(obj_projet.get_org()),
				'modals' : modals,
				'onglets' : onglets,
				'p' : obj_projet,
				'title' : 'Consulter un projet'
			})

	else :
		if 'action' in _req.GET :

			# Définition des paramètres
			if _req.GET['action'] == 'gerer-classes-ecole-projet' :
				params = [GererClassesEcoleProjet, obj_projet.get_cep().all()]
			elif _req.GET['action'] == 'gerer-tranche-age' :
				params = [GererTrancheAge, obj_projet.get_ta().all()]
			else :
				params = None

			if params :

				# Vérification du droit d'accès
				obj_util_connect.can_access(obj_projet.get_org(), False)

				# Soumission du formset
				formset = formset_factory(
					wraps(params[0])(partial(params[0], kw_projet = obj_projet))
				)(_req.POST)

				# Initialisation des erreurs
				erreurs = {}
				if not formset.is_valid() :
					for form in formset :
						for cle, val in form.errors.items() : erreurs['{}-{}'.format(form.prefix, cle)] = val

				if len(erreurs) == 0 :

					# Suppression de toutes les instances liées à une instance TProjet
					params[1].delete()

					# Création d'une instance
					for form in formset : form.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : 'Le projet a été modifié avec succès.', 'redirect' : '__RELOAD__'
						}}),
						content_type = 'application/json'
					)

				else :

					# Affichage des erreurs
					output = HttpResponse(json.dumps(erreurs), content_type = 'application/json')

	return output