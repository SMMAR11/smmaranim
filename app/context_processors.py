# coding: utf-8

def set_alerts(_req) :

	# Import
	from app.models import TReservation
	from app.models import TUtilisateur
	from datetime import date
	from django.core.urlresolvers import reverse
	from smmaranim.custom_settings import PKS
	from smmaranim.custom_settings import SMMAR_SUPPORT

	alertes = []

	# Initialisation des niveaux d'alertes
	niveaux = {
		1 : 'background-color: #FDEE00;',
		2 : 'background-color: #F8B862;',
		3 : 'background-color: #FF0921;'
	}

	# Obtention d'une instance TUtilisateur
	obj_util_connect = TUtilisateur.get_util_connect(_req)

	if obj_util_connect :
		for pm in obj_util_connect.get_org().get_pm().all() :

			# Renvoi d'une alerte en cas de dépassement du marché en animations ponctuelles
			if pm.get_nbre_dj_ap_rest_pm(False) < 0 :

				# Calcul du taux de dépassement
				taux = (abs(pm.get_nbre_dj_ap_rest_pm(False)) / pm.get_nbre_dj_ap_pm()) * 100

				# Stockage du niveau d'alerte
				if taux > 20 :
					niveau = 3
				elif taux > 10 :
					niveau = 2
				else :
					niveau = 1

				alertes.append({
					'descr_alert' : '''
					Le nombre de demi-journées prévues en animations ponctuelles a été dépassé de {} % pour le marché
					suivant : {}.
					'''.format('{0:g}'.format(taux), pm.get_marche()),
					'lien_alert' : '#',
					'nat_alert' : 'Dépassement du marché en animations ponctuelles',
					'niveau_alert' : [niveau, niveaux[niveau]]
				})

			# Renvoi d'une alerte en cas de dépassement du marché en programmes pédagogiques
			for elem in [pm.get_nbre_dj_pp_rest_pm(False, False), pm.get_nbre_dj_pp_rest_pm(True, False)] :
				if elem < 0 :

					# Calcul du taux de dépassement
					taux = (abs(elem) / pm.get_nbre_dj_pp_pm()) * 100

					# Stockage du niveau d'alerte
					if taux > 20 :
						niveau = 3
					elif taux > 10 :
						niveau = 2
					else :
						niveau = 1

					alertes.append({
						'descr_alert' : '''
						Le nombre de demi-journées prévues en programmes pédagogiques a été dépassé de {} % pour le
						marché suivant : {}.
						'''.format('{0:g}'.format(taux), pm.get_marche()),
						'lien_alert' : '#',
						'nat_alert' : 'Dépassement du marché en programmes pédagogiques',
						'niveau_alert' : [niveau, niveaux[niveau]]
					})

					# Sortie de la boucle si une alerte est déjà générée pour ce marché
					break

		if obj_util_connect.get_org().get_pk() == PKS['id_org__smmar'] and SMMAR_SUPPORT == True :

			# Stockage de la date du jour
			today = date.today() 

			for r in TReservation.objects.all() :

				# Empilement des actions
				actions = []
				if r.get_doit_chercher() == True :
					actions.append(['chercher', r.get_quand_chercher()])
				if r.get_doit_demonter() == True :
					actions.append(['démonter', r.get_quand_demonter()])
				if r.get_doit_livrer() == True :
					actions.append(['livrer', r.get_quand_livrer()])
				if r.get_doit_monter() == True :
					actions.append(['monter', r.get_quand_monter()])

				# Renvoi d'une alerte en cas d'actions à venir
				for elem in actions :
					if elem[1].date() >= today :

						# Stockage de la différence absolue entre la date du jour et la date de l'action
						diff = abs((today - elem[1].date()).days)

						# Stockage du niveau d'alerte
						if diff < 8 :
							niveau = 3
						elif diff < 16 :
							niveau = 2
						elif diff < 32 :
							niveau = 1
						else :
							niveau = None

						if niveau :
							alertes.append({
								'descr_alert' : '''
								Attention, le SMMAR doit {} l'outil suivant : {} (sauf si refus du SMMAR d'exécuter la
								tâche souhaitée par le demandeur).
								'''.format(elem[0], r.get_outil()),
								'lien_alert' : reverse('consult_reserv', args = [r.get_pk()]),
								'nat_alert' : 'Aides proposées par le SMMAR',
								'niveau_alert' : [niveau, niveaux[niveau]]
							})

	return {
		'alerts_list' : sorted(alertes, key = lambda l : (-l['niveau_alert'][0], l['nat_alert'])),
		'badge_color' : '#FF0921' if len(alertes) > 0 else '#82C46C'
	}

'''
Obtention des fichiers d'inclusion dans le template
_req : Objet requête
Retourne un tableau associatif
'''
def set_incls(_req) :

	# Import
	from app.functions.include_init import sub
	from smmaranim.custom_settings import INCLUDE_FILES
	from smmaranim.custom_settings import PDF_INCLUDE_FILES

	return {
		'body_includes' : ''.join([sub(elem) for elem in INCLUDE_FILES['body']]),
		'head_includes' : ''.join([sub(elem) for elem in INCLUDE_FILES['head']]),
		'pdf_includes' : ''.join([sub(elem) for elem in PDF_INCLUDE_FILES])
	}

'''
Obtention de constantes dans le template
_req : Objet requête
Retourne un tableau associatif
'''
def set_consts(_req) :

	# Import
	from app.apps import AppConfig
	from app.functions.modal_init import sub as modal_init
	from app.models import TUtilisateur
	from django.template.defaultfilters import safe

	# Tentative d'obtention d'une instance TUtilisateur
	obj_util_connect = TUtilisateur.get_util_connect(_req)

	# Déclaration des fenêtres modales permanentes
	if obj_util_connect :
		modals = [
			modal_init(
				'ger_mode_superadmin',
				'{} le mode super-administrateur'.format(
					'Activer' if obj_util_connect.get_est_superadmin() < 1 else 'Désactiver'
				)
			),
			modal_init('logout', 'Déconnexion de la plateforme {}'.format(AppConfig.verbose_name))
		]
	else :
		modals = []

	return {
		'app_name' : AppConfig.verbose_name,
		'connected_user' : TUtilisateur.get_util_connect(_req),
		'permanent_modals' : safe(''.join(modals))
	}

'''
Obtention des menus dans le template
_req : Objet requête
Retourne un tableau associatlf
'''
def set_menus(_req) :

	# Imports
	from app.models import TUtilisateur
	from django.core.urlresolvers import reverse

	output = {}

	# Initialisation du menu utilisateur
	obj_util = TUtilisateur.get_util_connect(_req)
	menu = obj_util.get_menu() if obj_util else {}

	# Préparation du menu principal
	elems = []
	for elem in menu.values() :

		# Mise en forme de l'élément
		if len(elem['mod_items']) > 0 :

			li = '''
			<li class="dropdown">
				<a class="dropdown-toggle" data-toggle="dropdown" href="#">
					{}
					<span class="caret"></span>
				</a>
				<ul class="dropdown-menu">{}</ul>
			</li>
			'''.format(
				elem['mod_name'],
				''.join(['<li><a href="{}">{}</a></li>'.format(
					'#' if not elem_2['item_url_name'] else \
					elem_2['item_url_name'].replace('__ABS__', '') if \
					elem_2['item_url_name'].startswith('__ABS__') else \
					reverse(elem_2['item_url_name']),
					elem_2['item_name']
				) for elem_2 in elem['mod_items'].values()])
			)
		else :
			li = '''
			<li><a href="{}">{}</a></li>
			'''.format(reverse(elem['mod_url_name']) if elem['mod_url_name'] else '#', elem['mod_name'])

		elems.append(li)

	output['top_menu'] = '<ul class="nav navbar-nav">{}</ul>'.format(''.join(elems))

	# Préparation du menu latéral
	elems = []
	for cle, val in menu.items() :

		# Début de paramétrage du panel
		params = {
			'mod_img' : val['mod_img'],
			'mod_href' : reverse(val['mod_url_name']) if val['mod_url_name'] else '#',
			'mod_name' : val['mod_name']
		}

		if len(val['mod_items']) > 0 :

			# Mise en forme du panel si sous-éléments
			panel = '''
			<div class="panel">
				<div class="panel-heading">
					<span class="panel-title">
						<a href="#pnl_{mod_key}" data-parent="#side-menu" data-toggle="collapse">
							<img src="{mod_img}">
							{mod_name}
						</a>
					</span>
				</div>
				<div class="collapse panel-collapse" id="pnl_{mod_key}">
					<div class="panel-body">
						<table>{mod_items}</table>
					</div>
				</div>
			</div>
			'''

			# Fin de paramétrage du panel
			params['mod_key'] = cle
			params['mod_items'] = ''.join(['<tr><td><a href="{}">{}</a></td></tr>'.format(
				'#' if not elem['item_url_name'] else \
				elem['item_url_name'].replace('__ABS__', '') if elem['item_url_name'].startswith('__ABS__') else \
				reverse(elem['item_url_name']),
				elem['item_name']
			) for elem in val['mod_items'].values()])

		else :

			# Mise en forme du panel si aucun sous-élément
			panel = '''
			<div class="panel">
				<div class="panel-heading">
					<span class="panel-title">
						<a href="{mod_href}">
							<img src="{mod_img}">
							{mod_name}
						</a>
					</span>
				</div>
			</div>
			'''

			# Fin de paramétrage du panel
			params['mod_href'] = reverse(val['mod_url_name']) if val['mod_url_name'] else '#'

		elems.append(panel.format(**params))

	output['side_menu'] = '<div class="panel-group" id="side-menu">{}</div>'.format(''.join(elems))

	return output