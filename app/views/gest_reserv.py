# coding: utf-8

# Import
from app.decorators import *

'''
Affichage du menu de gestion des réservations
_req : Objet requête
'''
@can_access('gest_reserv')
def get_menu(_req) :

	# Imports
	from app.functions.menu_init import sub as menu_init
	from django.shortcuts import render

	output = None

	if _req.method == 'GET' :

		# Affichage du template
		output = render(_req, './menu.html', {
			'menu' : menu_init(_req, 'gest_reserv', 2),
			'title' : 'Gestion des reservations'
		})

	return output

'''
Affichage du formulaire de gestion d'une réservation ou traitement d'une requête quelconque
_req : Objet requête
_inst : Ajout ou modification ?
'''
@can_access('gest_reserv')
def ger_reserv(_req, _inst) :

	# Imports
	from app.forms.gest_reserv import GererReservation
	from app.functions.form_init import sub as form_init
	from app.functions.modal_init import sub as modal_init
	from app.models import TReservation
	from app.models import TUtilisateur
	from django.core.urlresolvers import reverse
	from django.http import Http404
	from django.http import HttpResponse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from smmaranim.custom_settings import ALERTS
	from smmaranim.custom_settings import SMMAR_SUPPORT
	import json

	output = None

	# Tentative d'obtention d'une instance TReservation (si page de modification en cours)
	if _inst == False :
		obj_reserv = None
	else :
		if 'id' in _req.GET :
			obj_reserv = get_object_or_404(TReservation, pk = _req.GET['id'])
		else :
			raise Http404

	# Obtention d'une instance TUtilisateur
	obj_util_connect = TUtilisateur.get_util_connect(_req)

	# Vérification du droit d'accès
	if obj_reserv : obj_util_connect.can_access(obj_reserv.get_util().get_org(), False)

	if _req.method == 'GET' :

		# Initialisation du formulaire
		form_ger_reserv = GererReservation(instance = obj_reserv)

		# Définition du contenu de la balise <title/> (également utile à d'autres endroits)
		title = 'Modifier une réservation' if obj_reserv else 'Ajouter une réservation'

		# Affichage du template
		output = render(_req, './gest_reserv/ger_reserv.html', {
			'aides_smmar' : ALERTS['aides_smmar'],
			'form_ger_reserv' : form_init(form_ger_reserv),
			'modals' : [modal_init('ger_reserv', title)],
			'r' : obj_reserv,
			'support' : SMMAR_SUPPORT,
			'title' : title
		})

	else :

		# Soumission du formulaire
		form_ger_reserv = GererReservation(
			_req.POST,
			instance = obj_reserv,
			kw_dt_reserv = int(_req.POST.get('rb_dt_reserv')),
			kw_doit_chercher = 0 if not _req.POST.get('doit_chercher') else int(_req.POST.get('doit_chercher')),
			kw_doit_demonter = 0 if not _req.POST.get('doit_demonter') else int(_req.POST.get('doit_demonter')),
			kw_doit_livrer = 0 if not _req.POST.get('doit_livrer') else int(_req.POST.get('doit_livrer')),
			kw_doit_monter = 0 if not _req.POST.get('doit_monter') else int(_req.POST.get('doit_monter')),
			kw_util = obj_util_connect
		)

		if form_ger_reserv.is_valid() :

			# Création/modification d'une instance TReservation
			obj_reserv_valid = form_ger_reserv.save()

			# Affichage du message de succès
			output = HttpResponse(
				json.dumps({ 'success' : {
					'message' : 'La réservation a été {} avec succès.'.format('modifiée' if obj_reserv else 'ajoutée'),
					'redirect' : reverse('consult_reserv', args = [obj_reserv_valid.get_pk()])
				}}),
				content_type = 'application/json'
			)

		else :

			# Affichage des erreurs
			output = HttpResponse(json.dumps(form_ger_reserv.errors), content_type = 'application/json')

	return output

'''
Affichage de l'interface de choix d'une réservation ou traitement d'une requête quelconque
_req : Objet requête
'''
@can_access('gest_reserv')
def chois_reserv(_req) :

	# Imports
	from app.forms.gest_reserv import FiltrerReservation
	from app.functions.form_init import sub as form_init
	from app.functions.modal_init import sub as modal_init
	from app.models import TReservation
	from django.core.urlresolvers import reverse
	from django.http import HttpResponse
	from django.shortcuts import render
	import json

	output = None

	if _req.method == 'GET' :
		if 'action' in _req.GET :

			# Affichage d'une partie d'une réservation
			if _req.GET['action'] == 'consulter-reservation' and 'id' in _req.GET :

				# Obtention d'une instance TReservation
				obj_reserv = TReservation.objects.get(pk = _req.GET['id'])

				# Initialisation des attributs de la réservation
				attrs_reserv = obj_reserv.get_attrs_reserv()

				contenu = '''
				{}
				{}
				{}
				<div class="row">
					<div class="col-sm-6">{}</div>
					<div class="col-sm-6">{}</div>
				</div>
				<a href="{}" class="icon-with-text inform-icon">Consulter la réservation</a>
				'''.format(
					attrs_reserv['outil'],
					attrs_reserv['dt_reserv'],
					attrs_reserv['nom_complet_refer_reserv'],
					attrs_reserv['courr_refer_reserv'],
					attrs_reserv['tel_refer_reserv'],
					reverse('consult_reserv', args = [obj_reserv.get_pk()])
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
			form_filtr_reserv = FiltrerReservation()

			# Affichage du template
			output = render(_req, './gest_reserv/chois_reserv.html', {
				'cal_filtr_reserv' : form_filtr_reserv.get_calendar(_req),
				'form_filtr_reserv' : form_init(form_filtr_reserv),
				'modals' : [
					modal_init('affich_outil', 'Afficher l\'outil'),
					modal_init('consult_reserv', 'Consulter une partie d\'une réservation')
				],
				'title' : 'Choisir une réservation'
			})

	else :

		# Soumission du formulaire
		form_filtr_reserv = FiltrerReservation(_req.POST)

		# Mise à jour du calendrier ou affichage des erreurs
		if form_filtr_reserv.is_valid() :
			output = HttpResponse(
				json.dumps({ 'success' : { 'elements' : [['#za_cal_reserv', form_filtr_reserv.get_calendar(_req)]] }}),
				content_type = 'application/json'
			)
		else :
			output = HttpResponse(json.dumps(form_filtr_reserv.errors), content_type = 'application/json')

	return output

'''
Affichage des données d'une réservation ou traitement d'une requête quelconque
_req : Objet requête
_r : Instance TReservation ?
'''
@can_access('gest_reserv')
def consult_reserv(_req, _r) :

	# Imports
	from app.form_templates.gest_reserv import ger_expos
	from app.form_templates.gest_reserv import ger_rr
	from app.forms.gest_reserv import GererExposition
	from app.forms.gest_reserv import GererReferentReservation
	from app.functions.attributes_init import sub as attributes_init
	from app.functions.modal_init import sub as modal_init
	from app.functions.yes_or_no import sub as yes_or_no
	from app.models import TExposition
	from app.models import TReferentReservation
	from app.models import TReservation
	from app.models import TUtilisateur
	from django.http import HttpResponse
	from django.core.urlresolvers import reverse
	from django.shortcuts import get_object_or_404
	from django.shortcuts import render
	from smmaranim.custom_settings import ALERTS
	from smmaranim.custom_settings import SMMAR_SUPPORT
	import json

	output = None

	# Initialisation du préfixe de chaque formulaire
	prefix_ajout_rr = 'AjouterReferentReservation'
	prefix_modif_rr = 'ModifierReferentReservation'
	prefix_ajout_expos = 'AjouterExposition'
	prefix_modif_expos = 'ModifierExposition'

	# Tentative d'obtention d'une instance TReservation
	obj_reserv = get_object_or_404(TReservation, pk = _r)

	# Obtention d'une instance TUtilisateur
	obj_util_connect = TUtilisateur.get_util_connect(_req)

	if _req.method == 'GET' :
		if 'action' in _req.GET :

			# Initialisation du formulaire de modification d'un couple réservation/contact référent
			if _req.GET['action'] == 'initialiser-formulaire-modification-referent-reservation' and 'id' in _req.GET :

				# Obtention d'une instance TReferentReservation
				obj_rr = TReferentReservation.objects.get(pk = _req.GET['id'], id_reserv = obj_reserv)

				# Mise en session de l'identifiant du couple réservation/contact référent
				_req.session['treferentreservation__pk__update'] = obj_rr.get_pk()

				# Affichage du formulaire
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : ger_rr(_req, { 'instance' : obj_rr, 'prefix' : prefix_modif_rr })
					}}),
					content_type = 'application/json'
				)

			# Affichage d'une demande de suppression d'un couple réservation/contact référent
			if _req.GET['action'] == 'supprimer-referent-reservation-etape-1' and 'id' in _req.GET :

				# Obtention d'une instance TReferentReservation
				obj_rr = TReferentReservation.objects.get(pk = _req.GET['id'], id_reserv = obj_reserv)

				# Mise en session de l'identifiant du couple réservation/contact référent
				_req.session['treferentreservation__pk__delete'] = obj_rr.get_pk()

				# Affichage de la demande de suppression
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : yes_or_no(
							'?action=supprimer-referent-reservation-etape-2',
							'suppr_rr',
							[['Lieu(x) d\'exposition', obj_rr.get_expos().count()]]
						)
					}}),
					content_type = 'application/json'
				)

			# Suppression d'un couple réservation/contact référent
			if _req.GET['action'] == 'supprimer-referent-reservation-etape-2' \
			and 'treferentreservation__pk__delete' in _req.session :

				# Vérification du droit d'accès
				obj_util_connect.can_access(obj_reserv.get_util().get_org(), False)

				# Suppression d'une instance TReferentReservation
				TReferentReservation.objects.get(pk = _req.session.get('treferentreservation__pk__delete')).delete()

				# Suppression de la variable de session si définie
				if 'treferentreservation__pk__delete' in _req.session :
					del _req.session['treferentreservation__pk__delete']

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'Le contact référent a été supprimé avec succès.', 'redirect' : '__RELOAD__'
					}}),
					content_type = 'application/json'
				)

			# Consultation d'un lieu d'exposition
			if _req.GET['action'] == 'consulter-exposition' and 'id' in _req.GET :

				# Obtention d'une instance TExposition
				obj_expos = TExposition.objects.get(pk = _req.GET['id'], id_reserv = obj_reserv)

				# Initialisation des attributs du lieu d'exposition
				attrs_expos = attributes_init({
					'comm' : { 'label' : 'Commune accueillant l\'exposition', 'value' : obj_expos.get_comm() },
					'comm_expos' : { 'label' : 'Commentaire', 'value' : obj_expos.get_comm_expos() },
					'courr_rr' : {
						'label' : 'Courriel du contact référent', 'value' : obj_expos.get_rr().get_courr_rr()
					},
					'dt_expos' : { 'label' : 'Date(s) d\'exposition', 'value' : obj_expos.get_dt_expos__fr_str() },
					'lieu_expos' : { 'label' : 'Lieu d\'exposition', 'value' : obj_expos.get_lieu_expos() },
					'nom_complet_rr' : { 'label' : 'Nom complet du contact référent', 'value' : obj_expos.get_rr() },
					'outil' : { 'label' : 'Outil exposé', 'value' : obj_expos.get_reserv().get_outil() },
					'struct' : { 'label' : 'Structure d\'accueil', 'value' : obj_expos.get_struct() },
					'tel_rr' : {
						'label' : 'Numéro de téléphone du contact référent',
						'value' : obj_expos.get_rr().get_tel_rr__deconstructed()
					},
				})

				# Affichage des attributs
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : '''
						<div class="attributes-wrapper">
							{}
							{}
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
							{}
						</div>
						'''.format(
							attrs_expos['outil'],
							attrs_expos['struct'],
							attrs_expos['lieu_expos'],
							attrs_expos['comm'],
							attrs_expos['dt_expos'],
							attrs_expos['nom_complet_rr'],
							attrs_expos['courr_rr'],
							attrs_expos['tel_rr'],
							attrs_expos['comm_expos']
						)
					}}),
					content_type = 'application/json'
				)

			# Initialisation du formulaire de modification d'un lieu d'exposition
			if _req.GET['action'] == 'initialiser-formulaire-modification-exposition' and 'id' in _req.GET :

				# Obtention d'une instance TExposition
				obj_expos = TExposition.objects.get(pk = _req.GET['id'], id_reserv = obj_reserv)

				# Mise en session de l'identifiant de l'exposition
				_req.session['texposition__pk__update'] = obj_expos.get_pk()

				# Affichage du formulaire
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : ger_expos(
							_req, {
								'instance' : obj_expos,
								'prefix' : prefix_modif_expos,
								'kw_reserv' : obj_expos.get_reserv()
							}
						)
					}}),
					content_type = 'application/json'
				)

			# Affichage d'une demande de suppression d'un lieu d'exposition
			if _req.GET['action'] == 'supprimer-exposition-etape-1' and 'id' in _req.GET :

				# Obtention d'une instance TExposition
				obj_expos = TExposition.objects.get(pk = _req.GET['id'], id_reserv = obj_reserv)

				# Mise en session de l'identifiant du lieu d'exposition
				_req.session['texposition__pk__delete'] = obj_expos.get_pk()

				# Affichage de la demande de suppression
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : yes_or_no('?action=supprimer-exposition-etape-2', 'suppr_expos')
					}}),
					content_type = 'application/json'
				)

			# Suppression d'un lieu d'exposition
			if _req.GET['action'] == 'supprimer-exposition-etape-2' and 'texposition__pk__delete' in _req.session :

				# Vérification du droit d'accès
				obj_util_connect.can_access(obj_reserv.get_util().get_org(), False)

				# Suppression d'une instance TExposition
				TExposition.objects.get(pk = _req.session.get('texposition__pk__delete')).delete()

				# Suppression de la variable de session si définie
				if 'texposition__pk__delete' in _req.session : del _req.session['texposition__pk__delete']

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'Le lieu d\'exposition a été supprimé avec succès.', 'redirect' : '__RELOAD__'
					}}),
					content_type = 'application/json'
				)

			# Affichage d'une demande d'annulation de la réservation
			if _req.GET['action'] == 'annuler-reservation-etape-1' :

				# Affichage de la demande d'annulation
				output = HttpResponse(
					json.dumps({ 'success' : { 
						'modal_content' : yes_or_no('?action=annuler-reservation-etape-2', 'annul_reserv')
					}}),
					content_type = 'application/json'
				)

			# Annulation d'une réservation
			if _req.GET['action'] == 'annuler-reservation-etape-2' :

				# Vérification du droit d'accès
				obj_util_connect.can_access(obj_reserv.get_util().get_org(), False)

				# Suppression d'une instance TReservation
				obj_reserv.delete()

				# Affichage du message de succès
				output = HttpResponse(
					json.dumps({ 'success' : {
						'message' : 'La réservation a été annulée avec succès.', 'redirect' : reverse('chois_reserv')
					}}),
					content_type = 'application/json'
				)

			# Impression de la réservation
			if _req.GET['action'] == 'imprimer-reservation' :
				output = render(_req, './gest_reserv/imprim_reserv.html', {
					'aides_smmar' : ALERTS['aides_smmar'],
					'attrs_reserv' : obj_reserv.get_attrs_reserv(True),
					'support' : SMMAR_SUPPORT,
					'title' : 'Imprimer une réservation'
				})

		else :

			# Déclaration des fenêtres modales
			modals = [
				modal_init(
					'ajout_expos',
					'Ajouter un lieu d\'exposition',
					ger_expos(_req, { 'prefix' : prefix_ajout_expos, 'kw_reserv' : obj_reserv })
				),
				modal_init('ajout_rr', 'Ajouter un contact référent', ger_rr(_req, { 'prefix' : prefix_ajout_rr })),
				modal_init('annul_reserv', 'Êtes-vous sûr de vouloir annuler définitivement la réservation ?'),
				modal_init('consult_expos', 'Consulter un lieu d\'exposition'),
				modal_init('modif_rr', 'Modifier un contact référent'),
				modal_init('modif_expos', 'Modifier un lieu d\'exposition'),
				modal_init('suppr_expos', 'Êtes-vous sûr de vouloir supprimer définitivement le lieu d\'exposition ?'),
				modal_init('suppr_rr', 'Êtes-vous sûr de vouloir supprimer définitivement le contact référent ?')
			]

			# Affichage du template
			output = render(_req, './gest_reserv/consult_reserv.html', {
				'aides_smmar' : ALERTS['aides_smmar'],
				'attrs_reserv' : obj_reserv.get_attrs_reserv(),
				'can_access' : obj_util_connect.can_access(obj_reserv.get_util().get_org()),
				'modals' : modals,
				'r' : obj_reserv,
				'support' : SMMAR_SUPPORT,
				'title' : 'Consulter une réservation'
			})

	else :
		if 'action' in _req.GET :

			# Initialisation des paramètres du formulaire de gestion d'un couple réservation/contact référent
			if _req.GET['action'] == 'ajouter-referent-reservation' :
				params = { 'instance' : None, 'prefix' : prefix_ajout_rr }
			elif _req.GET['action'] == 'modifier-referent-reservation' :
				params = {
					'instance' : TReferentReservation.objects \
					.get(pk = _req.session.get('treferentreservation__pk__update')),
					'prefix' : prefix_modif_rr
				}
			else :
				params = None

			if params :

				# Vérification du droit d'accès
				obj_util_connect.can_access(obj_reserv.get_util().get_org(), False)

				# Soumission du formulaire
				form_ger_rr = GererReferentReservation(
					_req.POST, instance = params['instance'], prefix = params['prefix'], kw_reserv = obj_reserv
				)

				if form_ger_rr.is_valid() :

					# Suppression de la variable de session si définie
					if 'treferentreservation__pk__update' in _req.session :
						del _req.session['treferentreservation__pk__update']

					# Création/modification d'une instance TReferentReservation
					obj_rr_valid = form_ger_rr.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : '''
							Le contact référent a été {} avec succès.
							'''.format('modifié' if params['instance'] else 'ajouté'),
							'redirect' : '__RELOAD__'
						}}),
						content_type = 'application/json'
					)

				else :

					# Affichage des erreurs
					output = HttpResponse(
						json.dumps({
							'{}-{}'.format(form_ger_rr.prefix, cle) : val for cle, val in form_ger_rr.errors.items()
						}),
						content_type = 'application/json'
					)

			# Initialisation des paramètres du formulaire de gestion des lieux d'exposition
			if _req.GET['action'] == 'ajouter-exposition' :
				params = { 'instance' : None, 'prefix' : prefix_ajout_expos }
			elif _req.GET['action'] == 'modifier-exposition' :
				params = {
					'instance' : TExposition.objects \
					.get(pk = _req.session.get('texposition__pk__update')),
					'prefix' : prefix_modif_expos
				}
			else :
				params = None

			if params :

				# Vérification du droit d'accès
				obj_util_connect.can_access(obj_reserv.get_util().get_org(), False)

				# Soumission du formulaire
				form_ger_expos = GererExposition(
					_req.POST,
					instance = params['instance'],
					prefix = params['prefix'],
					kw_dt_expos = int(_req.POST.get('{}-rb_dt_expos'.format(params['prefix']))),
					kw_reserv = obj_reserv
				)

				if form_ger_expos.is_valid() :

					# Suppression de la variable de session si définie
					if 'texposition__pk__update' in _req.session : del _req.session['texposition__pk__update']

					# Création/modification d'une instance TExposition
					obj_expos_valid = form_ger_expos.save()

					# Affichage du message de succès
					output = HttpResponse(
						json.dumps({ 'success' : {
							'message' : '''
							Le lieu d'exposition a été {} avec succès.
							'''.format('modifié' if params['instance'] else 'ajouté'),
							'redirect' : '__RELOAD__'
						}}),
						content_type = 'application/json'
					)

				else :

					# Affichage des erreurs
					output = HttpResponse(
						json.dumps({'{}-{}'.format(
							form_ger_expos.prefix, cle
						) : val for cle, val in form_ger_expos.errors.items()}),
						content_type = 'application/json'
					)

	return output