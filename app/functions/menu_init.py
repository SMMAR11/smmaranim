# coding: utf-8

'''
Mise en forme d'un menu de vignettes
_req : Objet requête
_mod : Module source
_lim : Nombre de vignettes par ligne
Retourne une chaîne de caractères
'''
def sub(_req, _mod, _lim) :

	# Imports
	from app.models import TUtilisateur
	from django.core.urlresolvers import reverse
	from django.template.defaultfilters import safe

	# Obtention du menu utilisateur
	obj_util = TUtilisateur.get_util_connect(_req)
	menu = obj_util.get_menu() if obj_util else {}

	# Mise en forme d'une vignette
	thumbnail = '''
	<a class="custom-thumbnail" href="{}">
		<img src="{}">
		<div>{}</div>
	</a>
	'''

	# Initialisation des vignettes
	thumbnails = []
	if _mod == '__ALL__' :
		for elem in menu.values() :
			thumbnails.append(thumbnail.format(
				reverse(elem['mod_url_name']) if elem['mod_url_name'] else '#', elem['mod_img'], elem['mod_name']
			))
	else :
		if _mod in menu.keys() :
			for elem in menu[_mod]['mod_items'].values() :
				thumbnails.append(thumbnail.format(
					'#' if not elem['item_url_name'] else \
					elem['item_url_name'].replace('__ABS__', '') if elem['item_url_name'].startswith('__ABS__') else \
					reverse(elem['item_url_name']),
					elem['item_img'] or menu[_mod]['mod_img'],
					elem['item_name']
				))

	# Stockage du nombre de vignettes
	nbre_thumbnails = len(thumbnails)

	# Initialisation des lignes de vignettes
	rows = []

	# Préparation des lignes de vignettes complètes
	for i in range(nbre_thumbnails // _lim) :
		rows.append('<div class="row">{}</div>'.format(
			''.join(['<div class="col-sm-{}">{}</div>'.format(
				'{0:g}'.format(12 / _lim), thumbnails[i * _lim + j]
			) for j in range(_lim)]
		)))

	# Préparation de la ligne de vignettes incomplète
	nbre_thumbnails_manq = nbre_thumbnails % _lim
	if nbre_thumbnails_manq > 0 :
		rows.append('<div class="row">{}</div>'.format(
			''.join(['<div class="col-sm-{}">{}</div>'.format(
				'{0:g}'.format(12 / nbre_thumbnails_manq), thumbnails[i]
			) for i in range(nbre_thumbnails - nbre_thumbnails_manq, nbre_thumbnails)])
		))

	return safe('<div class="thumbnails-row">{}</div>'.format(''.join(rows)) if len(rows) > 0 else '')