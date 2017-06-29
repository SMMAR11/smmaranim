# coding: utf-8

# Import
from app.decorators import *

'''
Affichage du menu de gestion des marchés
_req : Objet requête
'''
@can_access('gest_marches')
def get_menu(_req) :

	# Imports
	from app.functions.menu_init import sub as menu_init
	from django.shortcuts import render

	output = None

	if _req.method == 'GET' :

		# Affichage du template
		output = render(_req, './menu.html', {
			'menu' : menu_init(_req, 'gest_marches', 2),
			'title' : 'Gestion des marchés'
		})

	return output

'''
Affichage du formulaire de gestion d'un marché ou traitement d'une requête quelconque
_req : Objet requête
_inst : Ajout ou modification ?
'''
@can_access('gest_marches')
def ger_marche(_req, _inst) :

	# Imports
	from app.forms.gest_marches import GererMarche
	from app.forms.gest_marches import GererPrestataireMarche
	from app.functions.form_init import sub as form_init
	from app.functions.modal_init import sub as modal_init
	from app.models import TMarche
	from django.core.urlresolvers import reverse
	from django.http import Http404
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	import json

	output = None

	# Tentative d'obtention d'une instance TMarche (si page de modification en cours)
	if _inst == False :
		obj_marche = None
	else :
		if 'id' in _req.GET :
			obj_marche = get_object_or_404(TMarche, pk = _req.GET['id'])
		else :
			raise Http404

	if _req.method == 'GET' :

		# Initialisation du formulaire
		form_ger_marche = GererMarche(instance = obj_marche)

		# Définition du contenu de la balise <title/> (également utile à d'autres endroits)
		title = 'Modifier un marché' if obj_marche else 'Ajouter un marché'

		# Affichage du template
		output = render(_req, './gest_marches/ger_marche.html', {
			'form_ger_marche' : form_init(form_ger_marche),
			'm' : obj_marche,
			'modals' : [modal_init('ger_marche', title)],
			'title' : title
		})

	else :

		# Soumission du formulaire
		form_ger_marche = GererMarche(_req.POST, instance = obj_marche)

		if form_ger_marche.is_valid() :

			# Création/modification d'une instance TMarche
			obj_marche_valid = form_ger_marche.save()

			# Affichage du message de succès
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'Le marché a été {} avec succès.'.format('modifié' if obj_marche else 'ajouté'),
					'redirect' : reverse('consult_marche', args = [obj_marche_valid.get_pk()])
				}}),
				content_type = 'application/json'
			)

		else :

			# Affichage des erreurs
			output = HttpResponse(json.dumps(form_ger_marche.errors), content_type = 'application/json')

	return output


'''
Affichage de l'interface de choix d'un marché ou traitement d'une requête quelconque
_req : Objet requête
'''
@can_access('gest_marches')
def chois_marche(_req) :

	# Imports
	from app.forms.gest_marches import FiltrerMarche
	from app.functions.datatable_reset import sub as datatable_reset
	from app.functions.form_init import sub as form_init
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	if _req.method == 'GET' :

		# Initialisation du formulaire
		form_filtr_marche = FiltrerMarche()

		# Affichage du template
		output = render(_req, './gest_marches/chois_marche.html', {
			'dtable_filtr_marche' : form_filtr_marche.get_datatable(_req),
			'form_filtr_marche' : form_init(form_filtr_marche),
			'title' : 'Choisir un marché'
		})

	else :

		# Soumission du formulaire
		form_filtr_marche = FiltrerMarche(_req.POST)

		# Réinitialisation de la datatable ou affichage des erreurs
		if form_filtr_marche.is_valid() :
			output = datatable_reset(form_filtr_marche.get_datatable(_req))
		else :
			output = HttpResponse(json.dumps(form_filtr_marche.errors), content_type = 'application/json')

	return output

'''
Affichage des données d'un marché ou traitement d'une requête quelconque
_req : Objet requête
_m : Instance TMarche ?
'''
@can_access('gest_marches')
def consult_marche(_req, _m) :

	# Imports
	from app.form_templates.gest_marches import ger_pm
	from app.forms.gest_marches import ChoisirPrestataireMarche
	from app.forms.gest_marches import GererPrestataireMarche
	from app.forms.gest_marches import GererTransactionDemiJournees
	from app.functions.attributes_init import sub as attributes_init
	from app.functions.datatable_reset import sub as datatable_reset
	from app.functions.form_init import sub as form_init
	from app.functions.modal_init import sub as modal_init
	from app.functions.yes_or_no import sub as yes_or_no
	from app.models import TAnimation
	from app.models import TMarche
	from app.models import TPrestatairesMarche
	from app.models import TProjet
	from app.models import TTransactionDemiJournees
	from django.core.urlresolvers import reverse
	from django.forms import formset_factory
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from django.template.context_processors import csrf
	from functools import partial
	from functools import wraps
	import json

	output = None

	# Tentative d'obtention d'une instance TMarche
	obj_marche = get_object_or_404(TMarche, pk = _m)

	# Initialisation du préfixe de chaque formulaire
	prefix_ajout_pm = 'AjouterPrestataireMarche'
	prefix_modif_pm = 'ModifierPrestataireMarche'
	prefix_chois_pm__gest_prep_real = 'ChoisirPrestataireMarche__GestionPreparationEtRealisation'
	prefix_chois_pm__projet = 'ChoisirPrestataireMarche__Projets'

	# Initialisation du préfixe de chaque formulaire de choix d'un prestataire
	prefixes_chois_pm = { 'gest_prep_real' : prefix_chois_pm__gest_prep_real, 'projet' : prefix_chois_pm__projet }

	if _req.method == 'GET' :
		if 'action' in _req.GET :

			# Initialisation du formulaire de modification d'un couple prestataire/marché
			if _req.GET['action'] == 'initialiser-formulaire-modification-prestataire' and 'id' in _req.GET :

				# Obtention d'une instance TPrestatairesMarche
				obj_pm = TPrestatairesMarche.objects.get(pk = _req.GET['id'], id_marche = obj_marche)

				# Mise en session de l'identifiant du couple prestataire/marché
				_req.session['tprestatairesmarche__pk__update'] = obj_pm.get_pk()

				# Affichage du formulaire
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : ger_pm(_req, {
							'instance' : obj_pm,
							'kw_marche' : obj_marche,
							'prefix' : prefix_modif_pm
						})
					}}),
					content_type = 'application/json'
				)

			# Affichage d'une demande de suppression d'un couple prestataire/marché
			if _req.GET['action'] == 'retirer-prestataire-etape-1' and 'id' in _req.GET :

				# Obtention d'une instance TPrestatairesMarche
				obj_pm = TPrestatairesMarche.objects.get(pk = _req.GET['id'], id_marche = obj_marche)

				# Mise en session de l'identifiant du couple prestataire/marché
				_req.session['tprestatairesmarche__pk__delete'] = obj_pm.get_pk()

				# Affichage de la demande de suppression
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : yes_or_no(
							'?action=retirer-prestataire-etape-2',
							'suppr_pm',
							[['Entrée(s) de demi-journées de préparation et de réalisation', obj_pm.get_tdj().count()]]
						)
					}}),
					content_type = 'application/json'
				)

			# Suppression d'un couple prestataire/marché
			if _req.GET['action'] == 'retirer-prestataire-etape-2' \
			and 'tprestatairesmarche__pk__delete' in _req.session :

				# Suppression d'une instance TPrestatairesMarche
				TPrestatairesMarche.objects.get(pk = _req.session.get('tprestatairesmarche__pk__delete')).delete()

				# Suppression de la variable de session si définie
				if 'tprestatairesmarche__pk__delete' in _req.session :
					del _req.session['tprestatairesmarche__pk__delete']

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'Le prestataire a été retiré du marché avec succès.', 'redirect' : '__RELOAD__'
					}}),
					content_type = 'application/json'
				)

			# Initialisation du formset relatif aux demi-journées de préparation et de réalisation
			if _req.GET['action'] == 'initialiser-formset-transactions-demi-journees' and 'id' in _req.GET :

				# Obtention d'une instance TPrestatairesMarche
				obj_pm = TPrestatairesMarche.objects.get(pk = _req.GET['id'], id_marche = obj_marche)

				# Mise en session de l'identifiant du couple prestataire/marché
				_req.session['ttransactiondemijournees__id_pm__update'] = obj_pm.get_pk()

				output = GererTransactionDemiJournees(kw_pm = obj_pm).get_datatable(_req)

			# Affichage d'une demande de suppression du marché
			if _req.GET['action'] == 'supprimer-marche-etape-1' :

				# Stockage du nombre de projets et d'animations susceptibles d'être supprimées en cascade
				projets = TProjet.objects.filter(id_pm__in = [pm.get_pk() for pm in obj_marche.get_pm().all()])
				anims = TAnimation.objects.filter(id_projet__in = [p.get_pk() for p in projets])
				tdjs = TTransactionDemiJournees.objects.filter(
					id_pm__in = [pm.get_pk() for pm in obj_marche.get_pm().all()]
				)

				# Affichage de la demande de suppression
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : yes_or_no(
							'?action=supprimer-marche-etape-2',
							'suppr_marche',
							[[
								'Projet(s)', projets.count()
							], [
								'Animation(s)', anims.count()
							], [
								'Demi-journée(s) de préparation et de réalisation', tdjs.count()
							]]
						)
					}}),
					content_type = 'application/json'
				)

			# Suppression du marché
			if _req.GET['action'] == 'supprimer-marche-etape-2' :

				# Suppression de l'instance TMarche
				obj_marche.delete()

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'Le marché a été supprimé avec succès.',
						'redirect' : reverse('chois_marche')
					}}),
					content_type = 'application/json'
				)
				
		else :

			# Initialisation des attributs du marché
			attrs_marche = {
				'dt_deb_marche' : {
					'label' : 'Date de début du marché', 'value' : obj_marche.get_dt_marche__str()[0]
				},
				'dt_fin_marche' : { 'label' : 'Date de fin du marché', 'value' : obj_marche.get_dt_marche__str()[1] },
				'int_marche' : { 'label' : 'Intitulé du marché', 'value' : obj_marche.get_int_marche() },
				'prest' : {
					'label' : 'Prestataire(s) lié(s) au marché',
					'value' : [[
						str(pm.get_prest()),
						pm.get_nbre_dj_ap_pm__str(),
						pm.get_nbre_dj_progr_pm('AP'),
						pm.get_nbre_dj_prep_real_pm(),
						pm.get_nbre_dj_ap_rest_pm(),
						pm.get_nbre_dj_pp_pm__str(),
						pm.get_nbre_dj_progr_pm('PP'),
						pm.get_nbre_dj_pp_rest_pm(),
						'''
						<span action="?action=initialiser-formset-transactions-demi-journees&id={}"
						class="half-icon icon-without-text" modal-suffix="ger_tdj" onclick="ajax(event);"
						title="Gérer les demi-journées de préparation et de réalisation"></span>
						'''.format(pm.get_pk()),
						'''
						<span action="?action=initialiser-formulaire-modification-prestataire&id={}"
						class="icon-without-text modify-icon" modal-suffix="modif_pm" onclick="ajax(event);"
						title="Modifier le prestataire"></span>
						'''.format(pm.get_pk()),
						'''
						<span action="?action=retirer-prestataire-etape-1&id={}"
						class="delete-icon icon-without-text" modal-suffix="suppr_pm" onclick="ajax(event);"
						title="Retirer le prestataire"></span>
						'''.format(pm.get_pk()),
					] for pm in obj_marche.get_pm().all()],
					'table' : True,
					'table_header' : [
						[
							['Nom', 'rowspan:3'],
							['Nombre de demi-journées', 'colspan:7'],
							['', 'rowspan:3'],
							['', 'rowspan:3'],
							['', 'rowspan:3']
						],
						[
							['Animations ponctuelles', 'colspan:4'],
							['Programmes pédagogiques', 'colspan:3']
						],
						[
							['Prévues', None],
							['Programmées', None],
							['De prép. et de réal.', None],
							['Restantes', None],
							['Prévues', None],
							['Programmées', None],
							['Restantes', None]
						]
					]
				}
			}

			# Initialisation des formulaires et des datatables
			donnees_chois_pm = { 'dtables' : {}, 'forms' : {} }
			for cle, val in prefixes_chois_pm.items() :
				form = ChoisirPrestataireMarche(prefix = val, kw_marche = obj_marche, kw_onglet = cle)
				donnees_chois_pm['dtables'][cle] = form.get_datatable(_req)
				donnees_chois_pm['forms'][cle] = form_init(form)

			# Déclaration des fenêtres modales
			modals = [
				modal_init(
					'ajout_pm',
					'Ajouter un prestataire au marché',
					ger_pm(_req, { 'kw_marche' : obj_marche, 'prefix' : prefix_ajout_pm })
				),
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
				modal_init('modif_pm', 'Modifier un prestataire'),
				modal_init('suppr_marche', 'Êtes-vous sûr de vouloir supprimer définitivement le marché ?'),
				modal_init('suppr_pm', 'Êtes-vous sûr de vouloir retirer définitivement le prestataire de ce marché ?')
			]

			# Affichage du template
			output = render(_req, './gest_marches/consult_marche.html', {
				'attrs_marche' : attributes_init(attrs_marche),
				'dtables_chois_pm' : donnees_chois_pm['dtables'],
				'forms_chois_pm' : donnees_chois_pm['forms'],
				'm' : obj_marche,
				'modals' : modals,
				'title' : 'Consulter un marché'
			})

	else :
		if 'action' in _req.GET :

			# Initialisation des paramètres du formulaire
			if _req.GET['action'] == 'ajouter-prestataire' :
				params = { 'instance' : None, 'prefix' : prefix_ajout_pm }
			elif _req.GET['action'] == 'modifier-prestataire' :
				params = {
					'instance' : TPrestatairesMarche.objects \
					.get(pk = _req.session.get('tprestatairesmarche__pk__update')),
					'prefix' : prefix_modif_pm
				}
			else :
				params = None

			if params :

				# Soumission du formulaire
				form_ger_pm = GererPrestataireMarche(
					_req.POST, instance = params['instance'], prefix = params['prefix'], kw_marche = obj_marche
				)

				if form_ger_pm.is_valid() :

					# Suppression de la variable de session si définie
					if 'tprestatairesmarche__pk__update' in _req.session :
						del _req.session['tprestatairesmarche__pk__update']

					# Création/modification d'une instance TPrestatairesMarche
					obj_pm_valid = form_ger_pm.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : '''
							Le prestataire a été {} avec succès.
							'''.format('modifié' if params['instance'] else 'ajouté au marché'),
							'redirect' : '__RELOAD__'
						}}),
						content_type = 'application/json'
					)

				else :

					# Affichage des erreurs
					output = HttpResponse(
						json.dumps({
							'{}-{}'.format(form_ger_pm.prefix, cle) : val for cle, val in form_ger_pm.errors.items()
						}),
						content_type = 'application/json'
					)

			# Initialisation des paramètres du formulaire
			if _req.GET['action'] == 'choisir-prestataire' :
				if 'onglet' in _req.GET :

					# Soumission du formulaire
					form_chois_pm = ChoisirPrestataireMarche(
						_req.POST,
						prefix = prefixes_chois_pm[_req.GET['onglet']],
						kw_marche = obj_marche,
						kw_onglet = _req.GET['onglet']
					)

					# Réinitialisation de la datatable ou affichage des erreurs
					if form_chois_pm.is_valid() :
						output = datatable_reset(form_chois_pm.get_datatable(_req))
					else :
						output = HttpResponse(
							json.dumps({ '{}-{}'.format(
								form_chois_pm.prefix, cle
							) : val for cle, val in form_chois_pm.errors.items() }),
							content_type = 'application/json'
						)

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
							'message' : 'Le prestataire a été modifié avec succès.', 'redirect' : '__RELOAD__'
						}}),
						content_type = 'application/json'
					)

				else :

					# Affichage des erreurs
					output = HttpResponse(json.dumps(erreurs), content_type = 'application/json')

	return output