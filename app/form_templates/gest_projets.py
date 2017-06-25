# coding: utf-8

'''
Obtention du formulaire de gestion d'une classe liée à une école d'un projet
_req : Objet requête
_kwargs : Arguments
Retourne une chaîne de caractères
'''
def ger_cep(_req, _kwargs) :

	# Imports
	from app.forms.gest_projets import GererClassesEcoleProjet
	from app.functions.form_init import sub as form_init
	from django.template.context_processors import csrf

	# Initialisation du formulaire
	form = form_init(GererClassesEcoleProjet(**_kwargs))

	return '''
	<form action="?action={}-classe-ecole-projet" method="post" name="form_{}_cep" onsubmit="ajax(event);">
		<input name="csrfmiddlewaretoken" type="hidden" value="{}">
		<div class="row">
			<div class="col-md-6">{}</div>
			<div class="col-md-6">{}</div>
		</div>
		<div class="row">
			<div class="col-md-6">{}</div>
			<div class="col-md-6">{}</div>
		</div>
		{}
		{}
		<button class="center-block custom-button main-button" type="submit">Valider</button>
	</form>
	'''.format(
		'modifier' if 'instance' in _kwargs else 'ajouter',
		'modif' if 'instance' in _kwargs else 'ajout',
		csrf(_req)['csrf_token'],
		form['id_classe'],
		form['id_ecole'],
		form['nom_refer_cep'],
		form['prenom_refer_cep'],
		form['courr_refer_cep'],
		form['tel_refer_cep']
	)