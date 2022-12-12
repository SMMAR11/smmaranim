# coding: utf-8

# Imports
from django import forms

class Bilan_Projets_Cible_JPS(forms.Form):

	# Import
	from smmaranim.custom_settings import EMPTY_VALUE

	# Filtres

	zl_projet_presta = forms.ChoiceField(
		choices=[EMPTY_VALUE],
		label='Organisme en charge du projet',
		required=False
	)

	zl_marche_lot = forms.ChoiceField(
		choices=[EMPTY_VALUE], label='Lot', required=False
	)

	zd_date_debut = forms.DateField(
		label='Animations du', required=False
	)

	zd_date_fin = forms.DateField(
		label='Animations au', required=False
	)

	zl_projet_es = forms.ChoiceField(
		choices=[EMPTY_VALUE],
		label='Établissement scolaire',
		required=False
	)

	zl_es_commune = forms.ChoiceField(
		choices=[EMPTY_VALUE], label='Commune', required=False
	)

	# Méthodes Django

	def __init__(self, *args, **kwargs):

		# Imports
		from app.models import TCommune
		from app.models import TEcole
		from app.models import TOrganisme
		from app.models import TPrestatairesMarche
		from app.models import TUtilisateur

		# Arguments
		self.rq = kwargs.pop('kwarg_rq')

		super().__init__(*args, **kwargs)

		# Organismes sélectionnables
		self.fields['zl_projet_presta'].choices += [
			(oOrg.pk, oOrg) for oOrg in TOrganisme.objects.all()
		]

		# Lots sélectionnables (tous si utilisateur SMMAR ou ceux
		# concernant l'organisme de l'utilisateur connecté)
		oOrg = TUtilisateur.get_util_connect(self.rq).get_org()
		if oOrg.get_est_prest():
			qsPm = oOrg.get_pm()
		else:
			qsPm = TPrestatairesMarche.objects.all()
		marcheLots = []
		for oPm in qsPm:
			marcheLots.append((oPm.pk, oPm))
		self.fields['zl_marche_lot'].choices += marcheLots

		# Établissements scolaires sélectionnables
		self.fields['zl_projet_es'].choices += [
			(oEco.pk, oEco) for oEco in TEcole.objects.all()
		]

		# Communes sélectionnables
		self.fields['zl_es_commune'].choices += [
			(oCom.pk, oCom) for oCom in TCommune.objects.all()
		]

	# Méthodes privées

	def __cleaned_data(self):

		"""Récupération des données nettoyées du formulaire"""

		# Imports
		from datetime import datetime

		# Clés
		keys = [
			'zl_projet_presta',
			'zl_marche_lot',
			'zd_date_debut',
			'zd_date_fin',
			'zl_projet_es',
			'zl_es_commune'
		]

		if not self.data:
			return {
				element: self.fields[element].initial for element in keys
			}
		else:
			return {
				element: self.cleaned_data.get(element) for element in keys
			}

	def __get_data(self):

		"""Récupération des données du tableau"""

		# Imports
		from django.urls import reverse

		# Initialisation des données
		data = []

		# Animations
		qsPro = self.__get_queryset()

		# Pour chaque enregistrement...
		for oPro in qsPro:

			# Lot
			oPm = oPro.get_pm()

			# Classes d'une école
			oCEP = oPro.get_cep().first()
			if oCEP:
				classesES = oCEP.get_ecole().get_nom_ecole()
				ESCommu = oCEP.get_ecole().get_comm()
			else:
				classesES = ''
				ESCommu = ''

			# Filtres date animation
			cleaned_data = self.__cleaned_data()
			proAniNbAnds = {}
			aniDateDebut = cleaned_data['zd_date_debut']
			if aniDateDebut:
				proAniNbAnds['dt_anim__gte'] = aniDateDebut
			aniDateFin = cleaned_data['zd_date_fin']
			if aniDateFin:
				proAniNbAnds['dt_anim__lte'] = aniDateFin

			# Définition des données
			_data = {
				'_link': '''
				<a
					href="{}"
					class="inform-icon pull-right"
					target="_blank"
					title="Consulter le projet"
				></a>
				'''.format(
					reverse('consult_projet', args=[oPro.pk])
				),
				'proPresta': oPro.get_org(),
				'proMarche': oPm.get_marche() if oPm else '',
				'marcheLot': oPm.get_prests() if oPm else '',
				'pro': oPro,
				'proAniNb': oPro.get_anim().filter(**proAniNbAnds).count(),
				'proClasses': oPro.get_cep().count(),
				'classesES': classesES,
				'ESCommu': ESCommu
			}

			# Empilement des données
			data.append(_data)

		return data

	def __get_datatable(self):

		"""Table HTML"""

		# Imports

		# Données filtrées
		data = self.__get_data()

		# Balise </tbody>
		trs = []
		for i in data:
			_tds = [
				i['proPresta'],
				i['proMarche'],
				i['marcheLot'],
				i['pro'],
				i['proAniNb'],
				i['proClasses'],
				i['classesES'],
				i['ESCommu'],
				i['_link']
			]
			tds = ''.join(['<td>{}</td>'.format(j) for j in _tds])
			tr = '<tr>{}</tr>'.format(tds)
			trs.append(tr)
		tbody = ''.join(trs)

		return '''
		<div
			class="custom-table"
			id="dtable_real_etats_Bilan_Projets_Cible_JPS"
		>
			<table border="1" bordercolor="#DDD">
				<thead>
					<tr>
						<th>Organisme en charge du projet</th>
						<th>Marché</th>
						<th>Lot</th>
						<th>Projet</th>
						<th>Nombre d'animations</th>
						<th>Classes</th>
						<th>Établissement scolaire</th>
						<th>Commune</th>
						<th></th>
					</tr>
				</thead>
				<tbody>{}</tbody>
			</table>
		</div>
		'''.format(tbody)

	def __get_form(self):

		"""Formulaire"""

		# Imports
		from app.functions.form_init import sub as form_init
		from django.template.context_processors import csrf

		# Initialisation des contrôles
		form = form_init(self)

		return '''
		<form
			action=""
			method="post"
			name="form_real_etats_Bilan_Projets_Cible_JPS"
			onsubmit="ajax(event);"
		>
			<input name="csrfmiddlewaretoken" type="hidden" value="{}">
			<fieldset class="my-fieldset">
				<legend>Filtrer par</legend>
				<div>
					{}
					{}
					{}
					{}
					{}
					{}
					<button
						class="center-block custom-button main-button"
						type="submit"
					>Valider</button>
				</div>
			</fieldset>
		</form>
		'''.format(
			csrf(self.rq)['csrf_token'],
			form['zl_projet_presta'],
			form['zl_marche_lot'],
			form['zd_date_debut'],
			form['zd_date_fin'],
			form['zl_projet_es'],
			form['zl_es_commune']
		)

	def __get_queryset(self):

		"""Jeu de données"""

		# Imports
		from app.models import TAnimation
		from app.models import TClassesEcoleProjet
		from app.models import TProjet

		# Initialisation des données
		data = []

		# Requête HTTP "GET"
		if not self.data:

			# Jeu de données vierge
			qsPro = TProjet.objects.none()

		# Requête HTTP "POST"
		else:

			# Récupération des données nettoyées du formulaire
			cleaned_data = self.__cleaned_data()

			# Filtres
			ands = {'id_type_public__int_type_public': 'Jeune public scolaire'}
			pks = []

			# Filtre "Organisme en charge du projet"
			proPresta = cleaned_data['zl_projet_presta']
			if proPresta:
				ands['id_org'] = proPresta

			# Filtre Lot"
			marcheLot = cleaned_data['zl_marche_lot']
			if marcheLot:
				ands['id_pm'] = marcheLot

			# Filtre "Animations du"
			aniDateDebut = cleaned_data['zd_date_debut']
			if aniDateDebut:
				pks.append(TAnimation.objects.filter(
					dt_anim__gte=aniDateDebut
				).values_list('id_projet', flat=True))

			# Filtre "Animations au"
			aniDateFin = cleaned_data['zd_date_fin']
			if aniDateFin:
				pks.append(TAnimation.objects.filter(
					dt_anim__lte=aniDateFin
				).values_list('id_projet', flat=True))

			# Filtre "Établissement scolaire"
			classesES = cleaned_data['zl_projet_es']
			if classesES:
				pks.append(TClassesEcoleProjet.objects.filter(
					id_ecole=classesES
				).values_list('id_projet', flat=True))

			# Filtre "Commune"
			ESCommu = cleaned_data['zl_es_commune']
			if ESCommu:
				pks.append(TClassesEcoleProjet.objects.filter(
					id_ecole__code_comm=ESCommu
				).values_list('id_projet', flat=True))

			# Filtre "pk__in"
			if pks:
				ands['pk__in'] = set(pks[0]).intersection(*pks)

			# Jeu de données filtré
			qsPro = TProjet.objects.filter(**ands)

		return qsPro

	# Méthodes publiques

	def get_datatable(self):
		"""Table HTML"""
		return self.__get_datatable()

	def get_form(self):
		"""Formulaire"""
		return self.__get_form()