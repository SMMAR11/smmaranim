# coding: utf-8

# Import
from app.decorators import *

'''
Affichage du menu de gestion des animations
_req : Objet requête
'''
@can_access('gest_anim')
def get_menu(_req) :

	# Imports
	from app.functions.menu_init import sub as menu_init
	from django.shortcuts import render

	output = None

	if _req.method == 'GET' :

		# Affichage du template
		output = render(_req, './menu.html', {
			'menu' : menu_init(_req, 'gest_anim', 2),
			'title' : 'Gestion des animations'
		})

	return output

'''
Affichage du formulaire de gestion d'une animation ou traitement d'une requête quelconque
_req : Objet requête
_inst : Ajout ou modification ?
'''
@can_access('gest_anim')
def ger_anim(_req, _inst) :

	# Imports
	from app.forms.gest_anim import GererAnimation
	from app.functions.form_init import sub as form_init
	from app.functions.modal_init import sub as modal_init
	from app.models import TAnimation
	from app.models import TUtilisateur
	from django.core.urlresolvers import reverse
	from django.http import Http404
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	import json

	output = None

	# Tentative d'obtention d'une instance TAnimation (si page de modification en cours)
	if _inst == False :
		obj_anim = None
	else :
		if 'id' in _req.GET :
			obj_anim = get_object_or_404(TAnimation, pk = _req.GET['id'])
		else :
			raise Http404

	# Obtention d'une instance TUtilisateur
	obj_util_connect = TUtilisateur.get_util_connect(_req)

	if _req.method == 'GET' :

		# Initialisation du formulaire
		form_ger_anim = GererAnimation(instance = obj_anim, kw_org = obj_util_connect.get_org())

		# Définition du contenu de la balise <title/> (également utile à d'autres endroits)
		title = 'Modifier une animation' if obj_anim else 'Ajouter une animation'

		# Affichage du template
		output = render(_req, './gest_anim/ger_anim.html', {
			'form_ger_anim' : form_init(form_ger_anim),
			'a' : obj_anim,
			'b' : obj_anim.get_bilan__object() if obj_anim else None,
			'modals' : [modal_init('ger_anim', title)],
			'title' : title
		})

	else :

		# Vérification du droit d'accès
		if obj_anim : obj_util_connect.can_access(obj_anim.get_projet().get_org(), False)

		# Soumission du formulaire
		form_ger_anim = GererAnimation(
			_req.POST,
			instance = obj_anim,
			kw_est_anim = int(_req.POST.get('est_anim')),
			kw_org = obj_util_connect.get_org()
		)

		if form_ger_anim.is_valid() :

			# Création/modification d'une instance TAnimation
			obj_anim_valid = form_ger_anim.save()

			# Affichage du message de succès
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'L\'animation a été {} avec succès.'.format('modifiée' if obj_anim else 'ajoutée'),
					'redirect' : reverse('consult_anim', args = [obj_anim_valid.get_pk()])
				}}),
				content_type = 'application/json'
			)

		else :

			# Affichage des erreurs
			output = HttpResponse(json.dumps(form_ger_anim.errors), content_type = 'application/json')

	return output

'''
Affichage de l'interface de choix d'une animation ou traitement d'une requête quelconque
_req : Objet requête
'''
@can_access('gest_anim')
def chois_anim(_req) :

	# Imports
	from app.forms.gest_anim import FiltrerAnimation
	from app.functions.form_init import sub as form_init
	from app.functions.modal_init import sub as modal_init
	from app.models import TAnimation
	from app.models import TUtilisateur
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	# Obtention d'une instance TUtilisateur
	obj_util_connect = TUtilisateur.get_util_connect(_req)

	if _req.method == 'GET' :
		if 'action' in _req.GET :

			# Affichage d'une partie d'une animation
			if _req.GET['action'] == 'consulter-animation' and 'id' in _req.GET :

				# Obtention d'une instance TAnimation
				obj_anim = TAnimation.objects.get(pk = _req.GET['id'])

				# Initialisation des attributs de l'animation
				attrs_anim = obj_anim.get_attrs_anim()

				contenu = '''
				<div class="row">
					<div class="col-sm-6">{}</div>
					<div class="col-sm-6">{}</div>
				</div>
				{}
				{}
				<div class="row">
					<div class="col-sm-6">{}</div>
					<div class="col-sm-6">{}</div>
				</div>
				<a href="{}" class="icon-with-text inform-icon">Consulter l'animation</a>
				'''.format(
					attrs_anim['prest'],
					attrs_anim['projet'],
					attrs_anim['dt_heure_anim'],
					attrs_anim['nat_anim'],
					attrs_anim['lieu_anim'],
					attrs_anim['comm'],
					reverse('consult_anim', args = [obj_anim.get_pk()])
				)

				# Affichage
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : contenu
					}}),
					content_type = 'application/json'
				)

		else :

			# Initialisation du formulaire
			form_filtr_anim = FiltrerAnimation(kw_util = obj_util_connect)

			# Affichage du template
			output = render(_req, './gest_anim/chois_anim.html', {
				'cal_filtr_anim' : form_filtr_anim.get_calendar(_req),
				'form_filtr_anim' : form_init(form_filtr_anim),
				'modals' : [modal_init('consult_anim', 'Consulter une partie d\'une animation')],
				'title' : 'Choisir une animation'
			})

	else :

		# Soumission du formulaire
		form_filtr_anim = FiltrerAnimation(_req.POST, kw_util = obj_util_connect)

		# Mise à jour du calendrier ou affichage des erreurs
		if form_filtr_anim.is_valid() :
			output = HttpResponse(
				json.dumps({ 'success' : { 'elements' : [['#za_cal_anim', form_filtr_anim.get_calendar(_req)]] } }),
				content_type = 'application/json'
			)
		else :
			output = HttpResponse(json.dumps(form_filtr_anim.errors), content_type = 'application/json')

	return output

'''
Affichage des données d'une animation ou traitement d'une requête quelconque
_req : Objet requête
_a : Instance TAnimation ?
'''
@can_access('gest_anim')
def consult_anim(_req, _a) :

	# Imports
	from app.form_templates.gest_anim import ger_bilan
	from app.forms.gest_anim import ClonerBilan
	from app.forms.gest_anim import GererBilan
	from app.forms.gest_anim import GererBilanAnimation
	from app.forms.gest_anim import GererPoint
	from app.functions.modal_init import sub as modal_init
	from app.functions.yes_or_no import sub as yes_or_no
	from app.models import TAnimation
	from app.models import TBilan
	from app.models import TUtilisateur
	from django.core.urlresolvers import reverse
	from django.forms import formset_factory
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from functools import partial
	from functools import wraps
	import json

	output = None

	# Tentative d'obtention d'une instance TAnimation
	obj_anim = get_object_or_404(TAnimation, pk = _a)

	# Tentative d'obtention d'une instance TBilan
	obj_bilan = obj_anim.get_bilan__object()

	# Obtention d'une instance TUtilisateur
	obj_util_connect = TUtilisateur.get_util_connect(_req)

	if _req.method == 'GET' :
		if 'action' in _req.GET :

			# Affichage d'une demande de suppression d'un bilan
			if _req.GET['action'] == 'supprimer-bilan-etape-1' :
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : yes_or_no('?action=supprimer-bilan-etape-2', 'suppr_bilan')
					}}),
					content_type = 'application/json'
				)

			# Suppression d'un bilan
			if _req.GET['action'] == 'supprimer-bilan-etape-2' :

				# Vérification du droit d'accès
				obj_util_connect.can_access(obj_bilan.get_util().get_org(), False)

				# Suppression d'instances TBilan/TBilanAnimation
				obj_anim.get_bilan().all().delete()

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'Le bilan a été supprimé avec succès.', 'redirect' : '__RELOAD__'
					}}),
					content_type = 'application/json'
				)

			# Affichage d'une demande de suppression d'une animation
			if _req.GET['action'] == 'supprimer-animation-etape-1' :
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : yes_or_no('?action=supprimer-animation-etape-2', 'suppr_anim')
					}}),
					content_type = 'application/json'
				)

			# Suppression d'une animation
			if _req.GET['action'] == 'supprimer-animation-etape-2' :

				# Vérification du droit d'accès
				obj_util_connect.can_access(obj_anim.get_projet().get_org(), False)

				# Suppression d'une instance TAnimation
				obj_anim.delete()

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'L\'animation a été supprimée avec succès.',
						'redirect' : reverse('chois_anim')
					}}),
					content_type = 'application/json'
				)

		else :

			# Stockage du titre de la fenêtre modale de gestion d'un bilan
			mt_ger_bilan = '{} le bilan'.format('Modifier' if obj_bilan else 'Ajouter')

			# Stockage des attributs du bilan
			attrs_bilan = None
			if obj_bilan :
				attrs_bilan = obj_bilan.get_ba().get_attrs_ba() if obj_bilan.get_ba() else obj_bilan.get_attrs_bilan()

			# Déclaration des fenêtres modales
			modals = [
				modal_init(
					'ger_bilan',
					mt_ger_bilan,
					ger_bilan(_req, { 'kw_anim' : obj_anim, 'instance' : obj_bilan })
				),
				modal_init('suppr_anim', 'Êtes-vous sûr de vouloir supprimer définitivement l\'animation ?'),
				modal_init(
					'suppr_bilan', 'Êtes-vous sûr de vouloir supprimer définitivement le bilan de l\'animation ?'
				)
			]

			# Affichage du template
			output = render(_req, './gest_anim/consult_anim.html', {
				'a' : obj_anim,
				'b' : obj_bilan,
				'attrs_anim' : obj_anim.get_attrs_anim(),
				'attrs_bilan' : attrs_bilan,
				'can_access' : obj_util_connect.can_access(obj_anim.get_projet().get_org()),
				'modals' : modals,
				'mt_ger_bilan' : mt_ger_bilan,
				'title' : 'Consulter une animation'
			})

	else :
		if 'action' in _req.GET :

			# Gestion du bilan
			if _req.GET['action'] == 'gerer-bilan' :

				# Vérification du droit d'accès
				obj_util_connect.can_access(obj_anim.get_projet().get_org(), False)

				# Initialisation des erreurs
				erreurs = {}
				
				if obj_anim.get_est_anim() == True :

					# Soumission du formulaire
					form_ger_bilan = GererBilanAnimation(
						_req.POST,
						_req.FILES,
						instance = obj_bilan.get_ba() if obj_bilan else None,
						kw_anim = obj_anim,
						kw_util = obj_util_connect
					)

					# Soumission du formset
					_GererPoint = formset_factory(
						wraps(GererPoint)(partial(GererPoint, kw_ba = obj_bilan.get_ba() if obj_bilan else None))
					)
					formset_ger_point = _GererPoint(_req.POST)

					# Empilement des erreurs du formset
					if not formset_ger_point.is_valid() :
						for form in formset_ger_point :
							for cle, val in form.errors.items() : erreurs['{}-{}'.format(form.prefix, cle)] = val

				else :

					# Soumission du formulaire
					form_ger_bilan = GererBilan(
						_req.POST, instance = obj_bilan, kw_anim = obj_anim, kw_util = obj_util_connect
					)

				# Empilement des erreurs du formulaire
				if not form_ger_bilan.is_valid() :
					for cle, val in form_ger_bilan.errors.items() : erreurs[cle] = val

				if len(erreurs) == 0 :

					# Création/modification d'une instance TBilan ou TBilanAnimation
					obj_bilan_valid = form_ger_bilan.save()

					# Suppression, puis création d'instances TPoint
					if obj_anim.get_est_anim() == True :
						obj_bilan_valid.get_point().all().delete()
						for form in formset_ger_point :
							obj_point_valid = form.save(commit = False)
							obj_point_valid.id_ba = obj_bilan_valid
							form.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : '''
							Le bilan de l'animation a été {} avec succès.
							'''.format('modifié' if obj_bilan else 'ajouté'),
							'redirect' : '__RELOAD__'
						}}),
						content_type = 'application/json'
					)

				else :

					# Affichage des erreurs
					output = HttpResponse(json.dumps(erreurs), content_type = 'application/json')

			# CLonage du bilan
			if _req.GET['action'] == 'cloner-bilan' :

				# Soumission du formulaire
				form_clon_bilan = ClonerBilan(
					_req.POST, kw_anim = obj_anim, prefix = 'ClonerBilan'
				)

				if form_clon_bilan.is_valid() :

					# Stockage des données du formulaire
					cleaned_data = form_clon_bilan.cleaned_data
					val_bilan = cleaned_data.get('zl_bilan')

					# Obtention d'une instance TBilan + tentative d'obtention d'une instance TBilanAnimation
					obj_bilan_clone = TBilan.objects.get(pk = val_bilan)
					obj_ba_clone = obj_bilan_clone.get_ba()

					# Initialisation des clones
					clonings = [{
						'field_id' : '#id_nom_refer_bilan',
						'field_value' : obj_bilan_clone.get_nom_refer_bilan(),
						'type' : 'text' 
					}, {
						'field_id' : '#id_prenom_refer_bilan',
						'field_value' : obj_bilan_clone.get_prenom_refer_bilan(),
						'type' : 'text' 
					}, {
						'field_id' : '#id_fonct_refer_bilan',
						'field_value' : obj_bilan_clone.get_fonct_refer_bilan(),
						'type' : 'text' 
					}, {
						'field_id' : '#id_struct_refer_bilan',
						'field_value' : obj_bilan_clone.get_struct_refer_bilan(),
						'type' : 'text' 
					}, {
						'field_id' : '#id_comm_bilan',
						'field_value' : obj_bilan_clone.get_comm_bilan(),
						'type' : 'text' 
					}]

					# Initialisation des formsets à réinitialiser
					formsets = []

					if obj_ba_clone :

						# Suite de l'initialisation des clones
						extra_clonings = [{
							'field_id' : '#id_titre_ba',
							'field_value' : obj_ba_clone.get_titre_ba(),
							'type' : 'text' 
						}, {
							'field_id' : '#id_nbre_pers_pres_ba',
							'field_value' : obj_ba_clone.get_nbre_pers_pres_ba(),
							'type' : 'text' 
						}, {
							'field_id' : '#id_nbre_pers_prev_ba',
							'field_value' : obj_ba_clone.get_nbre_pers_prev_ba(),
							'type' : 'text' 
						}, {
							'field_id' : '#id_theme_ba',
							'field_value' : obj_ba_clone.get_theme_ba(),
							'type' : 'text' 
						}, {
							'field_id' : '#id_themat_abord_ba',
							'field_value' : obj_ba_clone.get_themat_abord_ba(),
							'type' : 'text' 
						}, {
							'field_id' : '#id_deroul_ba',
							'field_value' : obj_ba_clone.get_deroul_ba(),
							'type' : 'text' 
						}, {
							'field_id' : 'en_inter',
							'field_value' : str(obj_ba_clone.get_en_inter()),
							'type' : 'radio' 
						}, {
							'field_id' : 'en_exter',
							'field_value' : str(obj_ba_clone.get_en_exter()),
							'type' : 'radio' 
						}, {
							'field_id' : 'eval_ba',
							'field_value' : obj_ba_clone.get_eval_ba(),
							'type' : 'radio' 
						}, {
							'field_id' : 'zcc_plaq',
							'field_value' : [p.get_pk() for p in obj_ba_clone.get_plaq().all()],
							'type' : 'checkbox' 
						}]

						# Suite de l'initialisation des clones (prise en compte des points positifs/négatifs)
						for index, p in enumerate(obj_ba_clone.get_point().all()) :
							extra_clonings += [{
								'field_id' : '#id_form-{}-int_point'.format(index),
								'field_value' : p.get_int_point(),
								'type' : 'text' 
							}, {
								'field_id' : '#id_form-{}-comm_neg_point'.format(index),
								'field_value' : p.get_comm_neg_point(),
								'type' : 'text' 
							}, {
								'field_id' : '#id_form-{}-comm_pos_point'.format(index),
								'field_value' : p.get_comm_pos_point(),
								'type' : 'text' 
							}]

						# Fin d'initialisation des clones
						clonings += extra_clonings

						# Empilement des formsets à réinitialiser
						formsets.append(['#formset_ger_point', obj_ba_clone.get_point().count()])

					# Clonage du formulaire
					output = HttpResponse(
						json.dumps({ 'success' : {
							'clonings' : clonings, 'reinit_formsets' : formsets
						}}), content_type = 'application/json'
					)

				else :

					# Affichage des erreurs
					output = HttpResponse(
						json.dumps({ '{}-{}'.format(
							form_clon_bilan.prefix, cle
						) : val for cle, val in form_clon_bilan.errors.items() }),
						content_type = 'application/json'
					)

	return output