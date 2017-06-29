# coding: utf-8

'''
Obtention du formulaire de gestion d'un bilan d'animation
_req : Objet requête
_kwargs : Arguments
Retourne une chaîne de caractères
'''
def ger_bilan(_req, _kwargs) :

	# Imports
	from app.forms.gest_anim import GererBilan
	from app.forms.gest_anim import GererBilanAnimation
	from app.forms.gest_anim import GererPoint
	from app.functions.form_init import sub as form_init
	from django.template.context_processors import csrf

	kwargs = { cle : val for cle, val in _kwargs.items() }

	if kwargs['kw_anim'].get_est_anim() == True :

		# Mise à jour de l'instance (TBilan -> TBilanAnimation)
		kwargs['instance'] = kwargs['instance'].get_ba() if kwargs['instance'] else None

		# Initialisation du formulaire
		form = form_init(GererBilanAnimation(**kwargs))

		# Initialisation du formset
		dtable_ger_point = GererPoint(kw_ba = kwargs['instance']).get_datatable(_req)

		# Mise en forme du formulaire
		content = '''
		<div class="custom-well form-well">Données générales de l'animation</div>
		{}
		<div class="row">
			<div class="col-md-6">{}</div>
			<div class="col-md-6">{}</div>
		</div>
		{}
		{}
		{}
		<div class="row">
			<div class="col-md-6">{}</div>
			<div class="col-md-6">{}</div>
		</div>
		<div class="custom-well form-well">Contact référent de l'animation</div>
		<div class="row">
			<div class="col-md-6">{}</div>
			<div class="col-md-6">{}</div>
		</div>
		<div class="row">
			<div class="col-md-6">{}</div>
			<div class="col-md-6">{}</div>
		</div>
		<div class="custom-well form-well">Ressenti de l'animation</div>
		{}
		{}
		<div class="custom-well form-well">Données complémentaires de l'animation</div>
		{}
		{}
		{}
		{}
		{}
		{}
		{}
		{}
		{}
		'''.format(
			form['titre_ba'],
			form['nbre_pers_pres_ba'],
			form['nbre_pers_prev_ba'],
			form['theme_ba'],
			form['themat_abord_ba'],
			form['deroul_ba'],
			form['en_inter'],
			form['en_exter'],
			form['nom_refer_bilan'],
			form['prenom_refer_bilan'],
			form['fonct_refer_bilan'],
			form['struct_refer_bilan'],
			form['eval_ba'],
			dtable_ger_point[0],
			form['zcc_plaq'],
			form['photo_1_ba'],
			form['photo_2_ba'],
			form['photo_3_ba'],
			form['rdp_1_ba'],
			form['rdp_2_ba'],
			form['rdp_3_ba'],
			form['outil_ba'],
			form['comm_bilan']
		)

		# Mise en forme du contenu hors-formulaire
		extra_content = dtable_ger_point[1]

	else :

		# Initialisation du formulaire
		form = form_init(GererBilan(**kwargs))

		content = '''
		<div class="row">
			<div class="col-md-6">{}</div>
			<div class="col-md-6">{}</div>
		</div>
		<div class="row">
			<div class="col-md-6">{}</div>
			<div class="col-md-6">{}</div>
		</div>
		{}
		'''.format(
			form['nom_refer_bilan'],
			form['prenom_refer_bilan'],
			form['fonct_refer_bilan'],
			form['struct_refer_bilan'],
			form['comm_bilan']
		)

		extra_content = ''

	return '''
	<form action="?action=gerer-bilan" enctype="multipart/form-data" method="post" name="form_ger_bilan"
	onsubmit="ajax(event);">
		<input name="csrfmiddlewaretoken" type="hidden" value="{}">
		{}
		<button class="center-block custom-button main-button" type="submit">Valider</button>
	</form>
	{}
	'''.format(csrf(_req)['csrf_token'], content, extra_content)