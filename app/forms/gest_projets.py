# coding: utf-8

# Import
from django import forms

class GererProjet(forms.ModelForm) :

	# Import
	from smmaranim.custom_settings import EMPTY_VALUE

	# Champ
	zl_pm = forms.ChoiceField(choices = [EMPTY_VALUE], label = 'Marché')
	zl_sti = forms.ChoiceField(
		choices = [EMPTY_VALUE],
		help_text = 'Si aucune option n\'est choisie, alors il s\'agit d\'une animation ponctuelle.',
		label = 'Événement',
		required = False
	)
	
	class Meta :

		# Import
		from app.models import TProjet

		fields = ['comm_projet', 'id_type_public', 'int_projet']
		model = TProjet

	def __init__(self, *args, **kwargs) :

		# Import
		from app.models import TTypeIntervention

		# Initialisation des arguments
		self.kw_util = kwargs.pop('kw_util')

		super(GererProjet, self).__init__(*args, **kwargs)

		# Suppression du champ "Marché" si un utilisateur n'appartenant à aucun prestataire est connecté
		if self.kw_util.get_org().get_est_prest() == False : del self.fields['zl_pm']

		# Définition des choix de chaque liste déroulante
		if 'zl_pm' in self.fields :
			self.fields['zl_pm'].choices += \
			[(pm.get_pk(), pm.get_marche()) for pm in self.kw_util.get_org().get_pm().all()]
		self.fields['zl_sti'].choices += \
		[[ti, [(sti.get_pk(), sti) for sti in ti.get_sti().all()]] for ti in TTypeIntervention.objects.all()]

		# Définition de la valeur initiale de chaque champ
		if self.instance.get_pk() :
			initial = {}
			if 'zl_pm' in self.fields and self.instance.get_pm() : initial['zl_pm'] = self.instance.get_pm().get_pk()
			if self.instance.get_sti() : initial['zl_sti'] = self.instance.get_sti().get_pk()
			for cle, val in initial.items() : self.fields[cle].initial = val

	def save(self, commit = True) :

		# Imports
		from app.models import TPrestatairesMarche
		from app.models import TSousTypeIntervention

		# Stockage des données du formulaire
		cleaned_data = self.cleaned_data
		val_pm = cleaned_data.get('zl_pm')
		val_sti = cleaned_data.get('zl_sti')

		# Création/modification d'une instance TProjet
		obj = super(GererProjet, self).save(commit = False)
		obj.id_org = self.kw_util.get_org()
		if val_pm : obj.id_pm = TPrestatairesMarche.objects.get(pk = val_pm)
		if val_sti : obj.id_sti = TSousTypeIntervention.objects.get(pk = val_sti)
		obj.save()

		# Suppression des instances TClassesEcoleProjet si le type de public visé n'est pas un public jeune
		if 'id_type_public' in self.changed_data : obj.get_cep().all().delete()

		return obj

class FiltrerProjet(forms.Form) :

	# Imports
	from app.models import TOrganisme
	from app.models import TTypeIntervention

	# Champs
	zl_org = forms.ModelChoiceField(label = 'Organisme', queryset = TOrganisme.objects.all(), required = False)
	zl_type_interv = forms.ModelChoiceField(
		label = 'Type d\'intervention', queryset = TTypeIntervention.objects.all(), required = False
	)

	def get_datatable(self, _req, *args, **kwargs) :

		# Imports
		from app.models import TProjet
		from django.core.urlresolvers import reverse

		# Stockage des données du formulaire
		if _req.method == 'GET' :
			val_org = self.fields['zl_org'].initial
			val_type_interv = self.fields['zl_type_interv'].initial
		else :
			cleaned_data = self.cleaned_data
			val_org = cleaned_data.get('zl_org')
			val_type_interv = cleaned_data.get('zl_type_interv')

		# Initialisation du jeu de données
		if val_org :
			projets = TProjet.objects.filter(id_org = val_org)
		else :
			projets = TProjet.objects.all()
		if val_type_interv :
			for p in projets :
				if p.get_type_interv() != val_type_interv : projets = projets.exclude(pk = p.get_pk())

		# Initialisation de la balise <tbody/>
		tbody = ''.join(['<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tr])) for tr in [[
			p.get_int_projet(),
			p.get_org(),
			p.get_type_interv(),
			p.get_sti() or '-',
			'''
			<a href="{}" class="inform-icon pull-right" title="Consulter le projet"></a>
			'''.format(reverse('consult_projet', args = [p.get_pk()]))
		] for p in projets]])

		return '''
		<div class="custom-table" id="dtable_chois_projet">
			<table border="1" bordercolor="#DDD">
				<thead>
					<tr>
						<th>Intitulé du projet</th>
						<th>Organisme</th>
						<th>Type d'intervention</th>
						<th>Événement</th>
						<th></th>
					</tr>
				</thead>
				<tbody>{}</tbody>
			</table>
		</div>
		'''.format(tbody)

class GererClassesEcoleProjet(forms.ModelForm) :
	
	class Meta :

		# Import
		from app.models import TClassesEcoleProjet

		fields = ['courr_refer_cep', 'id_classe', 'id_ecole', 'nom_refer_cep', 'prenom_refer_cep', 'tel_refer_cep']
		model = TClassesEcoleProjet

	def __init__(self, *args, **kwargs) :

		# Initialisation des arguments
		self.kw_projet = kwargs.pop('kw_projet', None)

		super(GererClassesEcoleProjet, self).__init__(*args, **kwargs)

	def clean(self) :

		# Stockage des données du formulaire
		cleaned_data = super(GererClassesEcoleProjet, self).clean()
		val_classe = cleaned_data.get('id_classe')
		val_ecole = cleaned_data.get('id_ecole')

		# Renvoi d'une erreur en cas de redondance d'une classe pour une école donnée
		ceps = self.kw_projet.get_cep().filter(id_classe = val_classe, id_ecole = val_ecole)
		if self.instance.get_pk() : ceps = ceps.exclude(pk = self.instance.get_pk())
		if ceps.count() > 0 :
			self.add_error('__all__', 'La classe a déjà été ajoutée pour cet établissement scolaire.')

	def save(self, commit = True) :

		# Création/modification d'une instance TClassesEcoleProjet
		obj = super(GererClassesEcoleProjet, self).save(commit = False)
		obj.id_projet = self.kw_projet
		obj.save()

		return obj