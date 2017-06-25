# coding: utf-8

'''
Obtention du formulaire de gestion d'un lieu d'exposition
_req : Objet requête
_kwargs : Arguments
Retourne une chaîne de caractères
'''
def ger_expos(_req, _kwargs) :

	# Imports
	from app.forms.gest_reserv import GererExposition
	from app.functions.form_init import sub as form_init
	from django.template.context_processors import csrf

	# Initialisation du formulaire
	form = GererExposition(**_kwargs)
	_form = form_init(form)

	# Définition d'un paramètre d'affichage des champs date
	tranche = 0 if 'instance' in _kwargs and not len(_kwargs['instance'].get_dt_expos()) > 1 else 1

	return '''
	<form action="?action={}-exposition" method="post" name="form_{}_expos" onsubmit="ajax(event);">
		<input name="csrfmiddlewaretoken" type="hidden" value="{}">
		{}
		<div class="row">
			<div class="col-sm-6">{}</div>
			<div class="col-sm-6">{}</div>
		</div>
		{}
		<div id="za_{}-dt_expos__on" style="{}">
			<div class="row">
				<div class="col-sm-6">{}</div>
				<div class="col-sm-6">{}</div>
			</div>
			<div class="row">
				<div class="col-sm-6">{}</div>
				<div class="col-sm-6">{}</div>
			</div>
		</div>
		<div id="za_{}-dt_expos__off" style="{}">
			<div class="row">
				<div class="col-sm-6">{}</div>
				<div class="col-sm-6">{}</div>
			</div>
		</div>
		{}
		{}
		<button class="center-block custom-button main-button" type="submit">Valider</button>
	</form>
	'''.format(
		'modifier' if 'instance' in _kwargs else 'ajouter',
		'modif' if 'instance' in _kwargs else 'ajout',
		csrf(_req)['csrf_token'],
		_form['id_struct'],
		_form['lieu_expos'],
		_form['zl_comm'],
		_form['rb_dt_expos'],
		form.prefix,
		'display: none;' if tranche == 0 else '',
		_form['zd_dt_deb_expos'],
		_form['zl_borne_dt_deb_expos'],
		_form['zd_dt_fin_expos'],
		_form['zl_borne_dt_fin_expos'],
		form.prefix,
		'display: none;' if tranche == 1 else '',
		_form['zd_dt_expos'],
		_form['zl_borne_dt_expos'],
		_form['zl_rr'],
		_form['comm_expos']
	)

'''
Obtention du formulaire de gestion d'un contact référent lié à une réservation
_req : Objet requête
_kwargs : Arguments
Retourne une chaîne de caractères
'''
def ger_rr(_req, _kwargs) :

	# Imports
	from app.forms.gest_reserv import GererReferentReservation
	from app.functions.form_init import sub as form_init
	from django.template.context_processors import csrf

	# Initialisation du formulaire
	form = form_init(GererReferentReservation(**_kwargs))

	return '''
	<form action="?action={}-referent-reservation" method="post" name="form_{}_rr" onsubmit="ajax(event);">
		<input name="csrfmiddlewaretoken" type="hidden" value="{}">
		<div class="row">
			<div class="col-md-6">{}</div>
			<div class="col-md-6">{}</div>
		</div>
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
		form['nom_rr'],
		form['prenom_rr'],
		form['courr_rr'],
		form['tel_rr']
	)