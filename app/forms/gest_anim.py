# coding: utf-8

# Import
from django import forms

class FiltrerAnimation(forms.Form) :

	# Import
	from smmaranim.custom_settings import MONTHS

	# Champs
	zl_org = forms.ModelChoiceField(label = 'Organisme', queryset = None, required = False)
	zl_mois = forms.ChoiceField(choices = [(index + 1, elem) for index, elem in enumerate(MONTHS)], label = 'Mois')
	zl_annee = forms.ChoiceField(label = 'Année')

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TOrganisme
		from datetime import date
		from smmaranim.custom_settings import YEAR_OF_CREATION

		# Initialisation des arguments
		self.kw_util = kwargs.pop('kw_util')

		super(FiltrerAnimation, self).__init__(*args, **kwargs)

		# Définition des choix de chaque liste déroulante, excepté celle des mois
		self.fields['zl_org'].queryset = \
		TOrganisme.objects.all() if 'A' in self.kw_util.get_type_util__list() else TOrganisme.objects.filter(
			pk = self.kw_util.get_org().get_pk()
		)
		self.fields['zl_annee'].choices = \
		[(elem, elem) for elem in range(date.today().year + 1, YEAR_OF_CREATION - 1, -1)]

		# Définition de la valeur initiale de chaque champ
		initial = { 'zl_org' : self.kw_util.get_org(), 'zl_mois' : date.today().month, 'zl_annee' : date.today().year }
		for cle, val in initial.items() : self.fields[cle].initial = val

		# Suppression de l'élément vide si l'utilisateur ne possède pas le rôle administrateur
		if 'A' not in self.kw_util.get_type_util__list() :
			self.fields['zl_org'].empty_label = None; self.fields['zl_org'].required = True

	def get_calendar(self, _req, *args, **kwargs) :

		# Imports
		from app.models import TAnimation
		from datetime import date
		from smmaranim.custom_settings import MONTHS
		import calendar

		# Stockage des données du formulaire
		if _req.method == 'GET' :
			val_org = self.fields['zl_org'].initial
			val_mois = self.fields['zl_mois'].initial
			val_annee = self.fields['zl_annee'].initial
		else :
			cleaned_data = self.cleaned_data
			val_org = cleaned_data.get('zl_org')
			val_mois = int(cleaned_data.get('zl_mois'))
			val_annee = int(cleaned_data.get('zl_annee'))

		# Obtention de l'indice du premier jour du mois ainsi que le nombre de jours composant celui-ci
		monthrange = calendar.monthrange(val_annee, val_mois)

		# Initialisation de deux variables : le quantième jour et sur quelle balise <td/> intervient le premier du
		# mois
		quant = 1
		prem = False

		# Initialisation des balises <tr/>
		trs = []

		for i in range(6) :

			# Initialisation des balises <td/>
			tds = []

			for j in range(7) :

				# Détermination de la balise <td/> correspondant au premier du mois
				if j == monthrange[0] and prem == False : prem = True

				# Mise en forme de la balise <td/>
				if prem == True and quant <= monthrange[1] :

					# Définition des conditions de la requête
					filters = { 'dt_anim' : date(val_annee, val_mois, quant) }
					if val_org : filters['id_projet__id_org'] = val_org

					# Stockage des animations programmées
					anims = TAnimation.objects.filter(**filters).order_by('heure_anim')

					td = '''
					<td class="mc-day">
						<span class="mcd-label">{}</span>
						<span class="mcd-content">{}</span>
					</td>
					'''.format(
						quant,
						''.join([
							'''
							<span action="?action=consulter-animation&id={}" class="mcd-rdv"
							modal-suffix="consult_anim" onclick="ajax(event);" style="color: {};" 
							title="Consulter une partie de l\'animation">{}</span>
							'''.format(a.get_pk(), a.get_projet().get_org().get_coul_org(), a) for a in anims
						])
					)

					# Incrémentation du quantième
					quant += 1

				else :
					td = '<td></td>'
					
				tds.append(td)
			trs.append('<tr>{}</tr>'.format(''.join(tds)))

		return '''
		<div id="za_cal_anim">
			<div class="month-calendar for-animations">
				<table border="1" bordercolor="#DDD">
					<thead>
						<tr><th colspan="7">{}</th></tr>
						<tr>
							<th>Lundi</th>
							<th>Mardi</th>
							<th>Mercredi</th>
							<th>Jeudi</th>
							<th>Vendredi</th>
							<th>Samedi</th>
							<th>Dimanche</th>
						</tr>
					</thead>
					<tbody>{}</tbody>
				</table>
			</div>
		</div>
		'''.format('{} {}'.format(MONTHS[val_mois - 1], val_annee),''.join(trs))

class GererAnimation(forms.ModelForm) :

	# Import
	from smmaranim.custom_settings import EMPTY_VALUE

	# Champs
	zl_projet = forms.ModelChoiceField(label = 'Projet', queryset = None)
	zh_heure_deb_anim = forms.TimeField(
		label = 'Heure de début de l\'animation <span class="fl-complement">(HH:MM)</span>'
	)
	zh_heure_fin_anim = forms.TimeField(
		label = 'Heure de fin de l\'animation <span class="fl-complement">(HH:MM)</span>', required = False
	)
	zl_comm = forms.ChoiceField(choices = [EMPTY_VALUE], label = 'Commune accueillant l\'animation')

	class Meta :

		# Import
		from app.models import TAnimation

		fields = ['dt_anim', 'est_anim', 'id_struct', 'lieu_anim', 'num_anim', 'nbre_dj_anim']
		model = TAnimation
		widgets = {
			'est_anim' : forms.RadioSelect(choices = [(0, 'Oui'), (1, 'Non')]),
			'num_anim' : forms.NumberInput(attrs = { 'may-be-required' : True })
		}

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.functions.get_communes import sub as get_communes
		from app.models import TProjet

		# Initialisation des arguments
		instance = kwargs.get('instance', None)
		kw_est_anim = kwargs.pop('kw_est_anim', None)
		kw_org = kwargs.pop('kw_org')

		# Mise en forme de certaines données
		if instance :
			initial = {
				'est_anim' : 0 if instance.get_est_anim() == False else 1,
				'nbre_dj_anim' : instance.get_nbre_dj_anim__str()
			}
		else :
			initial = { 'est_anim' : 1 }
		kwargs.update(initial = { **initial })

		super(GererAnimation, self).__init__(*args, **kwargs)

		# Définition des choix de chaque liste déroulante
		self.fields['zl_projet'].queryset = TProjet.objects.filter(id_org = kw_org)
		self.fields['zl_comm'].choices += get_communes()

		if self.instance.get_pk() :
			initial = {
				'zl_projet' : self.instance.get_projet(),
				'zh_heure_deb_anim' : self.instance.get_heure_anim__str()[0],
				'zh_heure_fin_anim' : self.instance.get_heure_anim__str()[-1] if len(
					self.instance.get_heure_anim__str()
				) > 1 else None,
				'zl_comm' : self.instance.get_comm().get_pk()
			}
			for cle, val in initial.items() : self.fields[cle].initial = val

		# Gestion du champ "Numéro de l'animation"
		if kw_est_anim is not None :
			if kw_est_anim == 1 :
				self.fields['num_anim'].required = True
			else :
				del self.fields['num_anim']

	def save(self, commit = True) :

		# Import
		from app.models import TCommune

		# Stockage des données du formulaire
		cleaned_data = self.cleaned_data
		val_projet = cleaned_data.get('zl_projet')
		val_heure_deb_anim = cleaned_data.get('zh_heure_deb_anim')
		val_heure_fin_anim = cleaned_data.get('zh_heure_fin_anim')
		val_num_anim = cleaned_data.get('num_anim')
		val_comm = cleaned_data.get('zl_comm')

		# Création/modification d'une instance TAnimation
		obj = super(GererAnimation, self).save(commit = False)
		obj.id_projet = val_projet
		obj.heure_anim = [val_heure_deb_anim, val_heure_fin_anim]
		obj.num_anim = val_num_anim
		obj.code_comm = TCommune.objects.get(pk = val_comm)
		obj.save()

		# Suppression du bilan si changement de nature d'animation
		if 'est_anim' in self.changed_data and obj.get_bilan__object() : obj.get_bilan().all().delete()

		return obj

class GererBilanAnimation(forms.ModelForm) :

	# Champ
	zcc_plaq = forms.MultipleChoiceField(
		label = 'Plaquette(s) distribuée(s)|Aperçu de la plaquette|Intitulé de la plaquette|__zcc__', required = False
	)

	class Meta :

		# Import
		from app.models import TBilanAnimation

		fields = [
			'comm_bilan',
			'deroul_ba',
			'en_exter',
			'en_inter',
			'eval_ba',
			'fonct_refer_bilan',
			'outil_ba',
			'nbre_pers_pres_ba',
			'nbre_pers_prev_ba',
			'nom_refer_bilan',
			'photo_1_ba',
			'photo_2_ba',
			'photo_3_ba',
			'prenom_refer_bilan',
			'rdp_1_ba',
			'rdp_2_ba',
			'rdp_3_ba',
			'struct_refer_bilan',
			'themat_abord_ba',
			'theme_ba',
			'titre_ba'
		]
		model = TBilanAnimation
		widgets = {
			'en_exter' : forms.RadioSelect(choices = [(True, 'Oui'), (False, 'Non')]),
			'en_inter' : forms.RadioSelect(choices = [(True, 'Oui'), (False, 'Non')]),
			'eval_ba' : forms.RadioSelect()
		}

	def __init__(self, *args, **kwargs) :

		# Import
		from app.models import TPlaquette

		# Initialisation des arguments
		self.kw_anim = kwargs.pop('kw_anim')
		self.kw_util = kwargs.pop('kw_util', None)

		super(GererBilanAnimation, self).__init__(*args, **kwargs)

		# Définition des choix de chaque liste déroulante
		self.fields['zcc_plaq'].choices = [(
			p.get_pk(),
			'|'.join([p.get_miniat_plaq__img({ 'height' : 40 }), p.get_int_plaq(), '__zcc__'])
		) for p in TPlaquette.objects.all()]

		# Définition de la valeur initiale de chaque champ
		if self.instance.get_pk() :
			self.fields['zcc_plaq'].initial = [p.get_pk() for p in self.instance.get_plaq().all()]

	def save(self, commit = True) :

		# Imports
		from app.models import TPlaquette
		from app.models import TPlaquettesDistribuees

		# Stockage des données du formulaire
		cleaned_data = self.cleaned_data
		val_plaq = cleaned_data.get('zcc_plaq')

		# Création/modification d'une instance TBilanAnimation
		obj = super(GererBilanAnimation, self).save(commit = False)
		obj.id_anim = self.kw_anim
		obj.id_util = self.kw_util
		obj.save()

		# Lien avec la table t_plaquette_distribuees
		obj.get_pd().all().delete()
		for p in val_plaq :
			TPlaquettesDistribuees.objects.create(id_ba = obj, id_plaq = TPlaquette.objects.get(pk = p))

		return obj

class GererBilan(forms.ModelForm) :

	class Meta :

		# Import
		from app.models import TBilan

		fields = ['comm_bilan', 'fonct_refer_bilan', 'nom_refer_bilan', 'prenom_refer_bilan', 'struct_refer_bilan']
		model = TBilan

	def __init__(self, *args, **kwargs) :

		# Initialisation des arguments
		self.kw_anim = kwargs.pop('kw_anim')
		self.kw_util = kwargs.pop('kw_util', None)

		super(GererBilan, self).__init__(*args, **kwargs)

	def save(self, commit = True) :

		# Création/modification d'une instance TBilan
		obj = super(GererBilan, self).save(commit = False)
		obj.id_anim = self.kw_anim
		obj.id_util = self.kw_util
		obj.save()

		return obj

class GererPoint(forms.ModelForm) :

	class Meta :

		# Import
		from app.models import TPoint

		fields = ['comm_neg_point', 'comm_pos_point', 'int_point']
		model = TPoint

	def __init__(self, *args, **kwargs) :

		# Initialisation des arguments
		self.kw_ba = kwargs.pop('kw_ba', None)

		super(GererPoint, self).__init__(*args, **kwargs)
		self.empty_permitted = False

	def save(self, commit = True) :

		# Création d'une instance TPoint
		obj = super(GererPoint, self).save(commit = False)
		if commit == True : obj.save()

		return obj

	def get_datatable(self, _req, *args, **kwargs) :

		# Imports
		from app.forms.gest_anim import GererPoint
		from app.functions.formset_init import sub as formset_init

		# Définition des valeurs initiales de chaque formulaire du formset si besoin
		initial = [{
			'comm_neg_point' : p.get_comm_neg_point(),
			'comm_pos_point' : p.get_comm_pos_point(),
			'int_point' : p.get_int_point()
		} for p in self.kw_ba.get_point().all()] if self.kw_ba else None

		# Initialisation du formset
		formset = formset_init(
			'ger_point',
			GererPoint,
			['Point(s) positif(s)/négatif(s) de l\'animation', False],
			'int_point|comm_pos_point|comm_neg_point',
			{ 'initial' : initial }
		)

		return formset