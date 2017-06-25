# coding: utf-8

'''
Obtention du formulaire de gestion d'un prestataire lié à un marché
_req : Objet requête
_kwargs : Arguments
Retourne une chaîne de caractères
'''
def ger_pm(_req, _kwargs) :

	# Imports
	from app.forms.gest_marches import GererPrestataireMarche
	from app.functions.form_init import sub as form_init
	from django.template.context_processors import csrf

	# Initialisation du formulaire
	form = form_init(GererPrestataireMarche(**_kwargs))

	return '''
	<form action="?action={}-prestataire" method="post" name="form_{}_pm" onsubmit="ajax(event);">
		<input name="csrfmiddlewaretoken" type="hidden" value="{}">
		{}
		<div class="row">
			<div class="col-md-6">{}</div>
			<div class="col-md-6">{}</div>
		</div>
		<button class="center-block custom-button main-button" type="submit">Valider</button>
	</form>
	'''.format(
		'modifier' if 'instance' in _kwargs else 'ajouter',
		'modif' if 'instance' in _kwargs else 'ajout',
		csrf(_req)['csrf_token'],
		form['zl_prest'],
		form['nbre_dj_ap_pm'],
		form['nbre_dj_pp_pm']
	)