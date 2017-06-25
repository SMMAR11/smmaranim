# coding: utf-8

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
					reverse(elem_2['item_url_name']) if elem_2['item_url_name'] else '#', elem_2['item_name']
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
				reverse(elem['item_url_name']) if elem['item_url_name'] else '#', elem['item_name']
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