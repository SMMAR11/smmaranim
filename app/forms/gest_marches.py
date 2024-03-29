# coding: utf-8

# Import
from django import forms

class GererMarche(forms.ModelForm) :
	
	# Champs
	zd_dt_deb_marche = forms.DateField(label = 'Date de début du marché <span class="fl-complement">(incluse)</span>')
	zd_dt_fin_marche = forms.DateField(label = 'Date de fin du marché <span class="fl-complement">(incluse)</span>')

	class Meta :

		# Import
		from app.models import TMarche

		fields = ['int_marche', 'diffe_ani_ponc_pro_peda_marche']
		model = TMarche
		widgets = {
			'diffe_ani_ponc_pro_peda_marche': forms.RadioSelect(
				choices = [(True, 'Oui'), (False, 'Non')]
			)
		}

	def __init__(self, *args, **kwargs) :
		super(GererMarche, self).__init__(*args, **kwargs)

		# Définition de la valeur initiale de chaque champ
		if self.instance.get_pk() :
			self.fields['zd_dt_deb_marche'].initial = self.instance.get_dt_marche()[0]
			self.fields['zd_dt_fin_marche'].initial = self.instance.get_dt_marche()[1]

	def clean(self) :

		# Stockage des données du formulaire
		cleaned_data = super(GererMarche, self).clean()
		val_dt_deb_marche = cleaned_data.get('zd_dt_deb_marche')
		val_dt_fin_marche = cleaned_data.get('zd_dt_fin_marche')

		if val_dt_deb_marche and val_dt_fin_marche and val_dt_deb_marche > val_dt_fin_marche :
			self.add_error('__all__', 'La date de début du marché doit être antérieure ou égale à la date de fin du marché.')

	def save(self, commit = True) :

		# Stockage des données du formulaire
		cleaned_data = self.cleaned_data
		val_dt_deb_marche = cleaned_data.get('zd_dt_deb_marche')
		val_dt_fin_marche = cleaned_data.get('zd_dt_fin_marche')

		# Création/modification d'une instance TMarche
		obj = super(GererMarche, self).save(commit = False)
		obj.dt_marche = [val_dt_deb_marche, val_dt_fin_marche]
		obj.save()

		return obj

class FiltrerMarche(forms.Form) :

	# Imports
	from app.models import TOrganisme
	from smmaranim.custom_settings import EMPTY_VALUE

	# Champs
	zl_prest = forms.ModelChoiceField(
		label = 'Prestataire', queryset = TOrganisme.objects.filter(est_prest = True), required = False
	)
	zl_annee_deb_marche = forms.ChoiceField(
		choices = [EMPTY_VALUE], label = 'Année de début du marché', required = False
	)
	zcc_sans_prest = forms.BooleanField(
		label = '''
		Afficher uniquement les marchés sans prestataire <span class="fl-complement">(toutes années confondues)</span>
		''',
		required = False,
		widget = forms.CheckboxInput()
	)

	def __init__(self, *args, **kwargs) :

		# Imports
		from datetime import date
		from smmaranim.custom_settings import YEAR_OF_CREATION

		super(FiltrerMarche, self).__init__(*args, **kwargs)

		# Définition des choix de la liste déroulante des années
		self.fields['zl_annee_deb_marche'].choices += \
		[(elem, elem) for elem in range(date.today().year + 1, YEAR_OF_CREATION - 1, -1)]

	def get_datatable(self, _req, *args, **kwargs) :

		# Imports
		from app.models import TMarche
		from django.urls import reverse

		# Stockage des données du formulaire
		if _req.method == 'GET' :
			val_prest = self.fields['zl_prest'].initial
			val_annee_deb_marche = self.fields['zl_annee_deb_marche'].initial
			val_sans_prest = self.fields['zcc_sans_prest'].initial
		else :
			cleaned_data = self.cleaned_data
			val_prest = cleaned_data.get('zl_prest')
			val_annee_deb_marche = cleaned_data.get('zl_annee_deb_marche')
			val_sans_prest = cleaned_data.get('zcc_sans_prest')

		# Initialisation du jeu de données des marchés
		if val_sans_prest :
			marches = [m for m in TMarche.objects.all() if m.get_prest().count() == 0]
		else :

			# Préparation des conditions de la requête
			filters = {}
			if val_prest : filters['tprestatairesmarche__id_prest'] = val_prest
			if val_annee_deb_marche : filters['dt_marche__0__year'] = val_annee_deb_marche

			marches = TMarche.objects.filter(**filters)

		# Initialisation de la balise <tbody/>
		tbody = ''.join(['<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tr])) for tr in [[
			m.get_int_marche(),
			*m.get_dt_marche__str(),
			m.get_prest__str(),
			'''
			<a href="{}" class="inform-icon pull-right" title="Consulter le marché"></a>
			'''.format(reverse('consult_marche', args = [m.get_pk()]))
		] for m in marches]])

		return '''
		<div class="custom-table" id="dtable_chois_marche">
			<table border="1" bordercolor="#DDD">
				<thead>
					<tr>
						<th>Intitulé du marché</th>
						<th>Date de début du marché</th>
						<th>Date de fin du marché</th>
						<th>Prestataire(s)</th>
						<th></th>
					</tr>
				</thead>
				<tbody>{}</tbody>
			</table>
		</div>
		'''.format(tbody)

class GererPrestataireMarche(forms.ModelForm) :

	# Champ
	zl_prest = forms.ModelChoiceField(
		label='Prestataire 1', queryset=None
	)
	zl_prest2 = forms.ModelChoiceField(
		label='Prestataire 2', queryset=None, required=False
	)

	class Meta :

		# Import
		from app.models import TPrestatairesMarche

		fields = [
			'numero_lot',
			'nbre_dj_ap_pm',
			'nbre_dj_pp_pm',
			'nbre_dj_ani_pm'
		]
		model = TPrestatairesMarche

	def __init__(self, *args, **kwargs) :

		# Import
		from app.models import TOrganisme

		# Initialisation des arguments
		self.kw_marche = kwargs.pop('kw_marche')

		super(GererPrestataireMarche, self).__init__(*args, **kwargs)

		# Définition des choix de la liste déroulante des prestataires
		prests = TOrganisme.objects.filter(est_prest=True)
		self.fields['zl_prest'].queryset = prests
		self.fields['zl_prest2'].queryset = prests

		# Personnalisation du champ prestataire
		if self.instance.get_pk() :
			self.fields['zl_prest'].initial = self.instance.get_prest()
			self.fields['zl_prest2'].initial = self.instance.get_prest2()

		# Gestion d'affichage des champs "Nombre de demi-journées"
		# selon le type de marché
		if self.kw_marche.diffe_ani_ponc_pro_peda_marche:
			del self.fields['nbre_dj_ani_pm']
		else:
			del self.fields['nbre_dj_ap_pm']
			del self.fields['nbre_dj_pp_pm']

	def save(self, commit = True) :

		# Stockage des données du formulaire
		cleaned_data = self.cleaned_data
		val_prest = cleaned_data.get('zl_prest')
		val_prest2 = cleaned_data.get('zl_prest2')

		# Création/modification d'une instance TPrestatairesMarche
		obj = super(GererPrestataireMarche, self).save(commit = False)
		obj.id_marche = self.kw_marche
		obj.id_prest = val_prest
		obj.id_prest2 = val_prest2
		obj.save()

		return obj

class ChoisirPrestataireMarche(forms.Form) :
	
	# Champ
	zl_prest = forms.ModelChoiceField(label = 'Prestataire', queryset = None)

	def __init__(self, *args, **kwargs) :

		# Import
		from app.models import TOrganisme

		# Initialisation des arguments
		self.kw_marche = kwargs.pop('kw_marche')
		self.kw_onglet = kwargs.pop('kw_onglet', None)

		super(ChoisirPrestataireMarche, self).__init__(*args, **kwargs)

		# Définition des choix de la liste déroulante des prestataires
		self.fields['zl_prest'].queryset = self.kw_marche.get_prest().all()

	def get_datatable(self, _req, *args, **kwargs) :

		# Import
		from app.models import TOrganisme
		from app.models import TProjet
		from django.urls import reverse

		# Stockage des données du formulaire
		val_prest = self.fields['zl_prest'].initial if _req.method == 'GET' else self.cleaned_data.get('zl_prest')

		# Instances TPrestatairesMarche
		if val_prest:
			qPm = self.kw_marche.get_pm().get_lots(oOrg=val_prest)
		else:
			qPm = None

		trs = []
		if self.kw_onglet == 'gest_prep_real' :

			# Empilement des balises <tr/>
			if val_prest and qPm:
				for pm in qPm:
					trs += [[
						tdj.get_pm().get_prests(),
						tdj.get_int_tdj(),
						tdj.get_nbre_dj_tdj_progr__str(),
						tdj.get_nbre_dj_tdj_util__str()
					] for tdj in pm.get_tdj().all()]

			# Mise en forme de la datatable
			output = '''
			<div class="custom-table" id="dtable_consult_tdj">
				<table border="1" bordercolor="#DDD">
					<thead>
						<tr>
							<th rowspan="2">Prestataire</th>
							<th rowspan="2">Intitulé</th>
							<th colspan="2">Nombre de demi-journées de préparation et de réalisation</th>
						</tr>
						<tr>
							<th>Programmées</th>
							<th>Utilisées</th>
						</tr>
					</thead>
					<tbody>{}</tbody>
				</table>
			</div>
			'''

		else :

			# Empilement des balises <tr/>
			if val_prest and qPm:
				trs += [[
					p.get_int_projet(),
					p.get_org(),
					p.get_type_interv(),
					p.get_sti() or '-',
					p.get_type_public(),
					'''
					<a href="{}" class="inform-icon pull-right" title="Consulter le projet"></a>
					'''.format(reverse('consult_projet', args = [p.get_pk()]))
				] for p in TProjet.objects.filter(id_org=val_prest, id_pm__in=qPm.values_list('id', flat=True))]


			output = '''
			<div class="custom-table" id="dtable_consult_projet">
				<table border="1" bordercolor="#DDD">
					<thead>
						<tr>
							<th>Intitulé du projet</th>
							<th>Organisme</th>
							<th>Type d'intervention</th>
							<th>Événement</th>
							<th>Type de public visé</th>
							<th>
						</tr>
					</thead>
					<tbody>{}</tbody>
				</table>
			</div>
			'''

		return output.format(
			''.join(['<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tr])) for tr in trs])
		)

class GererTransactionDemiJournees(forms.ModelForm) :

	class Meta :

		# Import
		from app.models import TTransactionDemiJournees

		fields = ['int_tdj', 'nbre_dj_tdj_progr', 'nbre_dj_tdj_util']
		model = TTransactionDemiJournees

	def __init__(self, *args, **kwargs) :

		# Initialisation des arguments
		self.kw_init = kwargs.pop('kw_init', False)
		self.kw_pm = kwargs.pop('kw_pm', None)

		super(GererTransactionDemiJournees, self).__init__(*args, **kwargs)
		self.empty_permitted = False

	def clean(self) :

		# Stockage des données du formulaire
		cleaned_data = super(GererTransactionDemiJournees, self).clean()
		val_int_tdj = cleaned_data.get('int_tdj')
		val_nbre_dj_tdj_progr = cleaned_data.get('nbre_dj_tdj_progr')
		val_nbre_dj_tdj_util = cleaned_data.get('nbre_dj_tdj_util')

		# Renvoi d'une erreur si utilisation > programmation
		if val_int_tdj and val_nbre_dj_tdj_progr is not None and val_nbre_dj_tdj_util is not None :
			if val_nbre_dj_tdj_util > val_nbre_dj_tdj_progr :
				self.add_error(
					'__all__',
					'''
					Veuillez saisir un nombre de demi-journées utilisées inférieur au nombre de demi-journées
					prévues pour la ligne dont l'intitulé est « {} ».
					'''.format(val_int_tdj)
				)

	def save(self, commit = True) :

		# Création d'une instance TTransactionDemiJournees
		obj = super(GererTransactionDemiJournees, self).save(commit = False)
		obj.id_pm = self.kw_pm
		obj.save()

		return obj

	def get_datatable(self, _req, *args, **kwargs) :

		# Imports
		from app.forms.gest_marches import GererTransactionDemiJournees
		from app.functions.datatable_reset import sub as datatable_reset
		from app.functions.formset_init import sub as formset_init

		# Définition des valeurs initiales de chaque formulaire du formset si besoin
		initial = [{
			'int_tdj' : tdj.get_int_tdj(),
			'nbre_dj_tdj_progr' : tdj.get_nbre_dj_tdj_progr__str(),
			'nbre_dj_tdj_util' : tdj.get_nbre_dj_tdj_util__str()
		} for tdj in self.kw_pm.get_tdj().all()] if self.kw_pm else None

		# Initialisation du formset
		formset = formset_init(
			'ger_tdj',
			GererTransactionDemiJournees,
			['', False],
			'int_tdj|nbre_dj_tdj_progr|nbre_dj_tdj_util',
			{ 'initial' : initial }
		)

		if self.kw_init == False :
			output = datatable_reset(formset[0], { 'modal_status' : 'show', 'reindex_formset' : True })
		else :
			output = formset

		return output