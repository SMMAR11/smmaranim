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

		fields = ['int_marche']
		model = TMarche

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
		from django.core.urlresolvers import reverse

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
	zl_prest = forms.ModelChoiceField(label = 'Prestataire', queryset = None)

	class Meta :

		# Import
		from app.models import TPrestatairesMarche

		fields = ['nbre_dj_ap_pm', 'nbre_dj_pp_pm']
		model = TPrestatairesMarche

	def __init__(self, *args, **kwargs) :

		# Import
		from app.models import TOrganisme

		# Initialisation des arguments
		self.kw_marche = kwargs.pop('kw_marche')

		super(GererPrestataireMarche, self).__init__(*args, **kwargs)

		# Initialisation des choix de la liste déroulante des prestataires
		if self.instance.get_pk() :
			prests = TOrganisme.objects.filter(pk = self.instance.get_prest().get_pk())
		else :
			prests = TOrganisme.objects \
			.filter(est_prest = True) \
			.exclude(pk__in = [pm.get_prest().get_pk() for pm in self.kw_marche.get_pm().all()])

		# Définition des choix de la liste déroulante des prestataires
		self.fields['zl_prest'].queryset = prests

		# Personnalisation du champ prestataire
		if self.instance.get_pk() :
			self.fields['zl_prest'].empty_label = None; self.fields['zl_prest'].initial = self.instance.get_prest()

	def save(self, commit = True) :

		# Stockage des données du formulaire
		cleaned_data = self.cleaned_data
		val_prest = cleaned_data.get('zl_prest')

		# Création/modification d'une instance TPrestatairesMarche
		obj = super(GererPrestataireMarche, self).save(commit = False)
		obj.id_marche = self.kw_marche
		obj.id_prest = val_prest
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

		# Stockage des données du formulaire
		val_prest = self.fields['zl_prest'].initial if _req.method == 'GET' else self.cleaned_data.get('zl_prest')

		trs = []
		if self.kw_onglet == 'gest_prep_real' :

			# Tentative d'obtention d'une instance TPrestatairesMarche
			obj_pm = self.kw_marche.get_pm().get(id_prest = val_prest) if val_prest else None

			if obj_pm :
				trs += [[
					tdj.get_pm().get_prest(),
					tdj.get_int_tdj(),
					tdj.get_nbre_dj_tdj__str()
				] for tdj in obj_pm.get_tdj().all()]

			# Mise en forme de la datatable
			output = '''
			<div class="custom-table" id="dtable_consult_tdj">
				<table border="1" bordercolor="#DDD">
					<thead>
						<tr>
							<th>Prestataire</th>
							<th>Intitulé</th>
							<th>Nombre de demi-journées de préparation et de réalisation</th>
						</tr>
					</thead>
					<tbody>{}</tbody>
				</table>
			</div>
			'''

		else :
			output = '''
			<div class="custom-table" id="dtable_consult_anim">
				<table border="1" bordercolor="#DDD">
					<thead><tr><th></th></tr></thead>
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

		fields = ['int_tdj', 'nbre_dj_tdj']
		model = TTransactionDemiJournees

	def __init__(self, *args, **kwargs) :

		# Initialisation des arguments
		self.kw_init = kwargs.pop('kw_init', False)
		self.kw_pm = kwargs.pop('kw_pm', None)

		super(GererTransactionDemiJournees, self).__init__(*args, **kwargs)
		self.empty_permitted = False

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
		from django.forms import formset_factory

		# Définition des valeurs initiales de chaque formulaire du formset si besoin
		initial = [{
			'int_tdj' : tdj.get_int_tdj(),
			'nbre_dj_tdj' : tdj.get_nbre_dj_tdj__str(),
		} for tdj in self.kw_pm.get_tdj().all()] if self.kw_pm else None

		# Initialisation du formset
		formset = formset_init(
			'ger_tdj', GererTransactionDemiJournees, ['', False], 'int_tdj|nbre_dj_tdj', { 'initial' : initial }
		)

		if self.kw_init == False :
			output = datatable_reset(formset[0], { 'modal_status' : 'show', 'reindex_formset' : True })
		else :
			output = formset

		return output