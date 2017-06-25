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

		# Affichage du template
		output = render(_req, './gest_projets/ger_projet.html', {
			'form_ger_projet' : form_init(form_ger_projet),
			'message__show' : True if obj_projet and \
			obj_projet.get_type_public().get_pk() == PKS['id_type_public__jp'] else False,
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
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	if _req.method == 'GET' :

		# Initialisation du formulaire
		form_filtr_projet = FiltrerProjet()

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
	from app.form_templates.gest_projets import ger_cep
	from app.functions.modal_init import sub as modal_init
	from app.functions.yes_or_no import sub as yes_or_no
	from app.models import TProjet
	from app.models import TClassesEcoleProjet
	from app.models import TUtilisateur
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
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

			# Impression du projet
			if _req.GET['action'] == 'imprimer-projet' :
				output = render(_req, './gest_projets/imprim_projet.html', {
					'attrs_projet' : obj_projet.get_attrs_projet(True), 'title' : 'Imprimer un projet'
				})

			# Initialisation du formulaire de modification d'un couple classe/école/projet
			if _req.GET['action'] == 'initialiser-formulaire-modification-classe-ecole-projet' and 'id' in _req.GET :

				# Obtention d'une instance TClassesEcoleProjet
				obj_cep = TClassesEcoleProjet.objects.get(pk = _req.GET['id'], id_projet = obj_projet)

				# Mise en session de l'identifiant du couple réservation/contact référent
				_req.session['tclassesecoleprojet__pk__update'] = obj_cep.get_pk()

				# Affichage du formulaire
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : ger_cep(_req, { 'instance' : obj_cep, 'prefix' : prefix_modif_cep })
					}}),
					content_type = 'application/json'
				)

			# Consultation d'une classe
			if _req.GET['action'] == 'consulter-classe-ecole-projet' and 'id' in _req.GET :

				# Obtention d'une instance TClassesEcoleProjet
				obj_cep = TClassesEcoleProjet.objects.get(pk = _req.GET['id'], id_projet = obj_projet)

				# Initialisation des attributs de la classe
				attrs_cep = obj_cep.get_attrs_cep()

				# Affichage des attributs
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : '''
						<div class="attributes-wrapper">
							<div class="row">
								<div class="col-sm-6">{}</div>
								<div class="col-sm-6">{}</div>
							</div>
							{}
							{}
							{}
						</div>
						'''.format(
							attrs_cep['id_classe'],
							attrs_cep['id_ecole'],
							attrs_cep['refer_cep'],
							attrs_cep['courr_refer_cep'],
							attrs_cep['tel_refer_cep']
						)
					}}),
					content_type = 'application/json'
				)

			# Affichage d'une demande de suppression d'un couple classe/école/projet
			if _req.GET['action'] == 'supprimer-classe-ecole-projet-etape-1' and 'id' in _req.GET :

				# Obtention d'une instance TClassesEcoleProjet
				obj_cep = TClassesEcoleProjet.objects.get(pk = _req.GET['id'], id_projet = obj_projet)

				# Mise en session de l'identifiant du couple classe/école/projet
				_req.session['tclassesecoleprojet__pk__delete'] = obj_cep.get_pk()

				# Affichage de la demande de suppression
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : yes_or_no('?action=supprimer-classe-ecole-projet-etape-2', 'suppr_cep')
					}}),
					content_type = 'application/json'
				)

			# Suppression d'un couple classe/école/projet
			if _req.GET['action'] == 'supprimer-classe-ecole-projet-etape-2' \
			and 'tclassesecoleprojet__pk__delete' in _req.session :

				# Vérification du droit d'accès
				obj_util_connect.can_access(obj_projet.get_org(), False)

				# Suppression d'une instance TClassesEcoleProjet
				TClassesEcoleProjet.objects.get(pk = _req.session.get('tclassesecoleprojet__pk__delete')).delete()

				# Suppression de la variable de session si définie
				if 'tclassesecoleprojet__pk__delete' in _req.session :
					del _req.session['tclassesecoleprojet__pk__delete']

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'La classe a été supprimée avec succès.', 'redirect' : '__RELOAD__'
					}}),
					content_type = 'application/json'
				)

		else :

			# Déclaration des fenêtres modales
			modals = [
				modal_init('ajout_cep', 'Ajouter une classe', ger_cep(_req, { 'prefix' : prefix_ajout_cep })),
				modal_init('consult_cep', 'Consulter une classe'),
				modal_init('modif_cep', 'Modifier une classe'),
				modal_init('suppr_cep', 'Êtes-vous sûr de vouloir supprimer définitivement la classe ?')
			]

			# Affichage du template
			output = render(_req, './gest_projets/consult_projet.html', {
				'attrs_projet' : obj_projet.get_attrs_projet(),
				'can_access' : obj_util_connect.can_access(obj_projet.get_org()),
				'ongl_cep__show' : True if obj_projet.get_type_public().get_pk() == PKS['id_type_public__jp'] else False,
				'modals' : modals,
				'p' : obj_projet,
				'title' : 'Consulter un projet'
			})

	else :
		if 'action' in _req.GET :

			# Initialisation des paramètres du formulaire de gestion d'un couple classe/école/projet
			if _req.GET['action'] == 'ajouter-classe-ecole-projet' :
				params = { 'instance' : None, 'prefix' : prefix_ajout_cep }
			elif _req.GET['action'] == 'modifier-classe-ecole-projet' :
				params = {
					'instance' : TClassesEcoleProjet.objects \
					.get(pk = _req.session.get('tclassesecoleprojet__pk__update')),
					'prefix' : prefix_modif_cep
				}
			else :
				params = None

			if params :

				# Vérification du droit d'accès
				obj_util_connect.can_access(obj_projet.get_org(), False)

				# Soumission du formulaire
				form_ger_cep = GererClassesEcoleProjet(
					_req.POST, instance = params['instance'], prefix = params['prefix'], kw_projet = obj_projet
				)

				if form_ger_cep.is_valid() :

					# Suppression de la variable de session si définie
					if 'tclassesecoleprojet__pk__update' in _req.session :
						del _req.session['tclassesecoleprojet__pk__update']

					# Création/modification d'une instance TClassesEcoleProjet
					obj_cep_valid = form_ger_cep.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : '''
							La classe a été {} avec succès.
							'''.format('modifiée' if params['instance'] else 'ajoutée'),
							'redirect' : '__RELOAD__'
						}}),
						content_type = 'application/json'
					)

				else :

					# Affichage des erreurs
					output = HttpResponse(
						json.dumps({
							'{}-{}'.format(form_ger_cep.prefix, cle) : val for cle, val in form_ger_cep.errors.items()
						}),
						content_type = 'application/json'
					)

	return output