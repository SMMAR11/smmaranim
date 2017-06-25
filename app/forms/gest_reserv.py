# coding: utf-8

# Import
from django import forms

class FiltrerReservation(forms.Form) :

	# Imports
	from smmaranim.custom_settings import EMPTY_VALUE
	from smmaranim.custom_settings import MONTHS

	# Champs
	zl_outil = forms.ChoiceField(
		choices = [EMPTY_VALUE],
		label = 'Outil|Aperçu de l\'outil|Intitulé|Description|__rb__',
		required = False,
		widget = forms.RadioSelect(attrs = { 'into-datatable' : None })
	)
	zl_mois = forms.ChoiceField(choices = [(index + 1, elem) for index, elem in enumerate(MONTHS)], label = 'Mois')
	zl_annee = forms.ChoiceField(label = 'Année')

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TOutil
		from datetime import date
		from smmaranim.custom_settings import YEAR_OF_CREATION

		super(FiltrerReservation, self).__init__(*args, **kwargs)

		# Définition des choix de chaque liste déroulante, excepté celle des mois
		self.fields['zl_outil'].choices += [(
			o.get_pk(),
			'|'.join([
				o.get_photo_outil__img({
					'action' : '?action=afficher-outil&id={}'.format(o.get_pk()),
					'class' : 'center-block show-picture',
					'height' : 40,
					'modal-suffix' : 'affich_outil',
					'onclick' : 'ajax(event);',
					'title' : 'Afficher l\'outil'
				}),
				o.get_int_outil(),
				o.get_descr_outil(),
				'__rb__'
			])
		) for o in TOutil.objects.all()]
		self.fields['zl_annee'].choices = \
		[(elem, elem) for elem in range(date.today().year + 1, YEAR_OF_CREATION - 1, -1)]

		# Définition de la valeur initiale de chaque champ
		self.fields['zl_mois'].initial = date.today().month
		self.fields['zl_annee'].initial = date.today().year

	def get_calendar(self, _req, *args, **kwargs) :

		# Imports
		from app.models import TReservation
		from app.models import TUtilisateur
		from datetime import date
		from smmaranim.custom_settings import MONTHS
		import calendar

		# Stockage des données du formulaire
		if _req.method == 'GET' :
			val_outil = self.fields['zl_outil'].initial
			val_mois = self.fields['zl_mois'].initial
			val_annee = self.fields['zl_annee'].initial
		else :
			cleaned_data = self.cleaned_data
			val_outil = cleaned_data.get('zl_outil')
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

					# Initialisation des réservations au jour J
					reservs = []

					if val_outil :

						# Stockage de la date courante de la boucle
						dt = date(val_annee, val_mois, quant)

						for r in TReservation.objects.filter(id_outil = val_outil) :
							if r.get_dt_reserv()[0] <= dt <= r.get_dt_reserv()[-1] :

								# Définition de la borne (<=> classe CSS)
								if dt == r.get_dt_reserv()[0] :
									borne = r.get_borne_dt_reserv()[0]
								elif dt == r.get_dt_reserv()[-1] :
									borne = r.get_borne_dt_reserv()[-1]
								else :
									borne = 'WD'

								# Préparation des attributs de la balise <div/>
								div_attrs = {
									'action' : '?action=consulter-reservation&id={}'.format(r.get_pk()),
									'class' : 'mcd-reservation {}'.format(borne.lower()),
									'modal-suffix' : 'consult_reserv',
									'onclick' : 'ajax(event);',
									'title' : 'Consulter une partie de la réservation'
								}

								# Ajout d'une classe CSS montrant que la réservation a été effectuée par un utilisateur
								# partageant le même organisme que l'utilisateur connecté
								if TUtilisateur.get_util_connect(_req).get_org() == r.get_util().get_org() :
									div_attrs['class'] += ' made-by-myself'

								# Mise en forme d'un bloc réservation
								div = '<div {}></div>'.format(
									''.join(['{}="{}"'.format(cle, val) for cle, val in div_attrs.items()])
								)

								# Empilement des réservations au jour J
								reservs.append(div)

					td = '''
					<td class="mc-day">
						<span class="mcd-label">{}</span>
						{}
					</td>
					'''.format(quant, ''.join(reservs))

					# Incrémentation du quantième
					quant += 1

				else :
					td = '<td></td>'
					
				tds.append(td)
			trs.append('<tr>{}</tr>'.format(''.join(tds)))

		return '''
		<div id="za_cal_reserv">
			<div class="month-calendar">
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

class GererReservation(forms.ModelForm) :

	# Imports
	from smmaranim.custom_settings import EMPTY_VALUE
	from smmaranim.custom_settings import RESERVATION_BOUNDS

	# Champs
	rb_dt_reserv = forms.ChoiceField(
		choices = [(1, 'Oui'), (0, 'Non')],
		initial = 0,
		label = 'La réservation se porte-t-elle uniquement sur une seule date ?',
		required = False,
		widget = forms.RadioSelect()
	)
	zd_dt_deb_reserv = forms.DateField(
		label = 'Date de début de la réservation <span class="fl-complement">(incluse)</span>'
	)
	zd_dt_fin_reserv = forms.DateField(
		label = 'Date de fin de la réservation <span class="fl-complement">(incluse)</span>'
	)
	zd_dt_reserv = forms.DateField(label = 'Date de la réservation')
	zl_borne_dt_deb_reserv = forms.ChoiceField(
		choices = [EMPTY_VALUE, RESERVATION_BOUNDS['WD'], RESERVATION_BOUNDS['PM']],
		label = 'Durée de début de la réservation'
	)
	zl_borne_dt_fin_reserv = forms.ChoiceField(
		choices = [EMPTY_VALUE, RESERVATION_BOUNDS['WD'], RESERVATION_BOUNDS['AM']],
		label = 'Durée de fin de la réservation'
	)
	zl_borne_dt_reserv = forms.ChoiceField(
		choices = [EMPTY_VALUE, RESERVATION_BOUNDS['WD'], RESERVATION_BOUNDS['AM'], RESERVATION_BOUNDS['PM']],
		label = 'Duree de la réservation'
	)

	class Meta :

		# Imports
		from app.models import TReservation
		from django.conf import settings

		fields = [
			'comm_reserv',
			'courr_refer_reserv',
			'doit_chercher',
			'doit_demonter',
			'doit_livrer',
			'doit_monter',
			'id_outil',
			'nom_refer_reserv',
			'ou_chercher',
			'ou_demonter',
			'ou_livrer',
			'ou_monter',
			'prenom_refer_reserv',
			'quand_chercher',
			'quand_demonter',
			'quand_livrer',
			'quand_monter',
			'tel_refer_reserv'
		]
		model = TReservation
		widgets = {
			'doit_chercher' : forms.RadioSelect(choices = [(1, 'Oui'), (0, 'Non')]),
			'doit_demonter' : forms.RadioSelect(choices = [(1, 'Oui'), (0, 'Non')]),
			'doit_livrer' : forms.RadioSelect(choices = [(1, 'Oui'), (0, 'Non')]),
			'doit_monter' : forms.RadioSelect(choices = [(1, 'Oui'), (0, 'Non')])
		}

	def __init__(self, *args, **kwargs) :

		# Initialisation des arguments
		instance = kwargs.get('instance', None)
		kw_dt_reserv = kwargs.pop('kw_dt_reserv', None)
		kw_doit_chercher = kwargs.pop('kw_doit_chercher', None)
		kw_doit_demonter = kwargs.pop('kw_doit_demonter', None)
		kw_doit_livrer = kwargs.pop('kw_doit_livrer', None)
		kw_doit_monter = kwargs.pop('kw_doit_monter', None)
		self.kw_util = kwargs.pop('kw_util', None)

		# Mise en forme de certaines données
		if instance :
			kwargs.update(initial = {
				'doit_chercher' : 0 if instance.get_doit_chercher() == False else 1,
				'doit_demonter' : 0 if instance.get_doit_demonter() == False else 1,
				'doit_livrer' : 0 if instance.get_doit_livrer() == False else 1,
				'doit_monter' : 0 if instance.get_doit_monter() == False else 1
			})

		super(GererReservation, self).__init__(*args, **kwargs)

		# Définition de la valeur initiale de chaque champ
		if self.instance.get_pk() :
			initial = { 'rb_dt_reserv' : 0 if len(self.instance.get_dt_reserv()) > 1 else 1 }
			if len(self.instance.get_dt_reserv()) > 1 :
				initial['zd_dt_deb_reserv'] = self.instance.get_dt_reserv()[0]
				initial['zd_dt_fin_reserv'] = self.instance.get_dt_reserv()[-1]
				initial['zl_borne_dt_deb_reserv'] = self.instance.get_borne_dt_reserv()[0]
				initial['zl_borne_dt_fin_reserv'] = self.instance.get_borne_dt_reserv()[-1]
			else :
				initial['zd_dt_reserv'] = self.instance.get_dt_reserv()[0]
				initial['zl_borne_dt_reserv'] = self.instance.get_borne_dt_reserv()[0]
			for cle, val in initial.items() : self.fields[cle].initial = val

		# Initialisation de tableaux (champs à exclure + champs requis)
		deleted = []
		required = []

		# Gestion des champs date
		if kw_dt_reserv is not None :
			if kw_dt_reserv == 0 :
				deleted += ['zd_dt_reserv', 'zl_borne_dt_reserv']
			else :
				deleted += ['zd_dt_deb_reserv', 'zd_dt_fin_reserv', 'zl_borne_dt_deb_reserv', 'zl_borne_dt_fin_reserv']
		
		# Gestion des champs "Quand ?" et "Où ?"
		t = [
			[kw_doit_chercher, ['ou_chercher', 'quand_chercher']],
			[kw_doit_demonter, ['ou_demonter', 'quand_demonter']],
			[kw_doit_livrer, ['ou_livrer', 'quand_livrer']],
			[kw_doit_monter, ['ou_monter', 'quand_monter']]
		]
		for elem in t :
			if elem[0] is not None :
				if elem[0] == 0 :
					deleted += elem[1]
				else :
					required += elem[1]

		# Traitements de champs
		for elem in deleted : del self.fields[elem]
		for elem in required : self.fields[elem].required = True

	def clean(self) :

		# Imports
		from app.functions.get_date_range import sub as get_date_range
		from datetime import date

		# Stockage des données du formulaire
		cleaned_data = super(GererReservation, self).clean()
		val_outil = cleaned_data.get('id_outil')
		val_dt_deb_reserv = cleaned_data.get('zd_dt_deb_reserv')
		val_dt_fin_reserv = cleaned_data.get('zd_dt_fin_reserv')
		val_dt_reserv = cleaned_data.get('zd_dt_reserv')
		val_borne_dt_deb_reserv = cleaned_data.get('zl_borne_dt_deb_reserv')
		val_borne_dt_fin_reserv = cleaned_data.get('zl_borne_dt_fin_reserv')
		val_borne_dt_reserv = cleaned_data.get('zl_borne_dt_reserv')

		# Vérification du/des champ(s) date
		erreur = None
		if val_dt_reserv :
			if self.kw_util.get_en_mode_superadmin() == False and val_dt_reserv < date.today() :
				erreur = ['CT', 'zd_dt_reserv']
		if val_dt_deb_reserv and val_dt_fin_reserv :
			if self.kw_util.get_en_mode_superadmin() == False and val_dt_deb_reserv < date.today() :
				erreur = ['CT', '__all__']
			elif val_dt_deb_reserv >= val_dt_fin_reserv : erreur = ['ODD', '__all__']

		# Initialisation des messages d'erreur
		codes = {
			'CT' : 'Veuillez respecter une cohérence temporelle.',
			'ODD' : '''
			Veuillez ordonner correctement la date de début de la réservation et la date de fin de la réservation.
			'''
		}

		if erreur :
			self.add_error(erreur[1], codes[erreur[0]])
		else :

			# Initialisation du paramètre de la fonction get_date_range
			if val_dt_reserv and val_borne_dt_reserv :
				t = { 'dates' : [val_dt_reserv], 'bounds' : [val_borne_dt_reserv] }
			elif val_dt_deb_reserv and val_dt_fin_reserv and val_borne_dt_deb_reserv and val_borne_dt_fin_reserv :
				t = {
					'dates' : [val_dt_deb_reserv, val_dt_fin_reserv],
					'bounds' : [val_borne_dt_deb_reserv, val_borne_dt_fin_reserv]
				}
			else :
				t = {}

			if val_outil and t :

				# Initialisation des conflits de dates
				conflits = []

				# Stockage de la rangée de dates
				rangee_dt_reserv = get_date_range(t)

				# Initialisation des réservations déjà effectuées
				reservs = val_outil.get_reserv().all()
				if self.instance.get_pk() : reservs = reservs.exclude(pk = self.instance.get_pk())

				for r in reservs :

					# Stockage de la rangée de dates de l'instance TReservation courante
					rangee_r = get_date_range({ 'dates' : r.get_dt_reserv(), 'bounds' : r.get_borne_dt_reserv() })

					# Empilement des conflits de dates
					for elem_dt_reserv in rangee_dt_reserv :
						for elem_r in rangee_r :
							if elem_dt_reserv[0] == elem_r[0] : conflits.append([elem_dt_reserv, elem_r])

				# Vérification d'un éventuel conflit tout court
				erreur = False
				for elem in conflits :
					if 'WD' in [elem[0][1], elem[1][1]] :
						erreur = True
					else :
						if elem[0][1] == elem[1][1] : erreur = True
				if erreur == True : self.add_error('id_outil', 'L\'outil est déjà réservé.')

	def save(self, commit = True) :

		# Stockage des données du formulaire
		cleaned_data = self.cleaned_data
		val_dt_deb_reserv = cleaned_data.get('zd_dt_deb_reserv')
		val_dt_fin_reserv = cleaned_data.get('zd_dt_fin_reserv')
		val_dt_reserv = cleaned_data.get('zd_dt_reserv')
		val_borne_dt_deb_reserv = cleaned_data.get('zl_borne_dt_deb_reserv')
		val_borne_dt_fin_reserv = cleaned_data.get('zl_borne_dt_fin_reserv')
		val_borne_dt_reserv = cleaned_data.get('zl_borne_dt_reserv')

		# Initialisation de la valeur des attributs dt_reserv et borne_dt_reserv
		if val_dt_reserv and val_borne_dt_reserv :
			t = { 'dt_reserv' : [val_dt_reserv], 'borne_dt_reserv' : [val_borne_dt_reserv] }
		else :
			t = {
				'dt_reserv' : [val_dt_deb_reserv, val_dt_fin_reserv],
				'borne_dt_reserv' : [val_borne_dt_deb_reserv, val_borne_dt_fin_reserv]
			}

		# Création/modification d'une instance TReservation
		obj = super(GererReservation, self).save(commit = False)
		obj.borne_dt_reserv = t['borne_dt_reserv']
		obj.dt_reserv = t['dt_reserv']
		obj.id_util = self.kw_util
		obj.save()

		return obj

class GererReferentReservation(forms.ModelForm) :

	class Meta :

		# Import
		from app.models import TReferentReservation

		fields = ['courr_rr', 'nom_rr', 'prenom_rr', 'tel_rr']
		model = TReferentReservation

	def __init__(self, *args, **kwargs) :

		# Initialisation des arguments
		self.kw_reserv = kwargs.pop('kw_reserv', None)

		super(GererReferentReservation, self).__init__(*args, **kwargs)

	def save(self, commit = True) :

		# Création/modification d'une instance TReferentReservation
		obj = super(GererReferentReservation, self).save(commit = False)
		obj.id_reserv = self.kw_reserv
		obj.save()

		return obj

class GererExposition(forms.ModelForm) :

	# Imports
	from smmaranim.custom_settings import EMPTY_VALUE
	from smmaranim.custom_settings import RESERVATION_BOUNDS

	# Champs
	zl_comm = forms.ChoiceField(choices = [EMPTY_VALUE], label = 'Commune accueillant l\'exposition')
	rb_dt_expos = forms.ChoiceField(
		choices = [(1, 'Oui'), (0, 'Non')],
		initial = 0,
		label = 'L\'exposition se porte-t-elle uniquement sur une seule date ?',
		required = False,
		widget = forms.RadioSelect()
	)
	zd_dt_deb_expos = forms.DateField(
		label = 'Date de début d\'exposition <span class="fl-complement">(incluse)</span>'
	)
	zd_dt_fin_expos = forms.DateField(
		label = 'Date de fin d\'exposition <span class="fl-complement">(incluse)</span>'
	)
	zd_dt_expos = forms.DateField(label = 'Date d\'exposition')
	zl_borne_dt_deb_expos = forms.ChoiceField(
		choices = [EMPTY_VALUE, RESERVATION_BOUNDS['WD'], RESERVATION_BOUNDS['PM']],
		label = 'Durée de début d\'exposition'
	)
	zl_borne_dt_fin_expos = forms.ChoiceField(
		choices = [EMPTY_VALUE, RESERVATION_BOUNDS['WD'], RESERVATION_BOUNDS['AM']],
		label = 'Durée de fin d\'exposition'
	)
	zl_borne_dt_expos = forms.ChoiceField(
		choices = [EMPTY_VALUE, RESERVATION_BOUNDS['WD'], RESERVATION_BOUNDS['AM'], RESERVATION_BOUNDS['PM']],
		label = 'Duree d\'exposition'
	)
	zl_rr = forms.ModelChoiceField(label = 'Contact référent', queryset = None)

	class Meta :

		# Import
		from app.models import TExposition

		fields = ['comm_expos', 'id_struct', 'lieu_expos']
		model = TExposition

	def __init__(self, *args, **kwargs) :

		# Imports
		from app.models import TCommune
		from smmaranim.custom_settings import DEPARTMENTS

		# Initialisation des arguments
		kw_dt_expos = kwargs.pop('kw_dt_expos', None)
		self.kw_reserv = kwargs.pop('kw_reserv')

		super(GererExposition, self).__init__(*args, **kwargs)

		# Initialisation des communes
		communes = [[c.get_pk(), c] for c in TCommune.objects.order_by('nom_comm')]

		# Initialisation des communes par département
		departs = sorted([[j for j in communes if j[0][:2] == i] for i in set(map(lambda l : l[0][:2], communes))])

		# Initialisation des choix de la liste déroulante des communes
		zl_comm__choices = []
		for d in departs :

			# Stockage du numéro du département
			num = d[0][0][:2]

			# Empilement des choix de la liste déroulante des communes par filtrage par rapport au numéro de
			# département
			if num in DEPARTMENTS.keys() : zl_comm__choices.append([DEPARTMENTS[num], [c for c in d]])

		# Définition des choix de chaque liste déroulante
		self.fields['zl_comm'].choices += zl_comm__choices
		self.fields['zl_rr'].queryset = self.kw_reserv.get_rr().all()

		# Définition de la valeur initiale de chaque champ
		if self.instance.get_pk() :
			initial = { 'rb_dt_expos' : 0 if len(self.instance.get_dt_expos()) > 1 else 1 }
			if len(self.instance.get_dt_expos()) > 1 :
				initial['zd_dt_deb_expos'] = self.instance.get_dt_expos()[0]
				initial['zd_dt_fin_expos'] = self.instance.get_dt_expos()[-1]
				initial['zl_borne_dt_deb_expos'] = self.instance.get_borne_dt_expos()[0]
				initial['zl_borne_dt_fin_expos'] = self.instance.get_borne_dt_expos()[-1]
			else :
				initial['zd_dt_expos'] = self.instance.get_dt_expos()[0]
				initial['zl_borne_dt_expos'] = self.instance.get_borne_dt_expos()[0]
			initial['zl_comm'] = self.instance.get_comm().get_pk()
			initial['zl_rr'] = self.instance.get_rr().get_pk()
			for cle, val in initial.items() : self.fields[cle].initial = val

		# Gestion des champs date
		if kw_dt_expos is not None :
			if kw_dt_expos == 0 :
				champs = ['zd_dt_expos', 'zl_borne_dt_expos']
			else :
				champs = ['zd_dt_deb_expos', 'zd_dt_fin_expos', 'zl_borne_dt_deb_expos', 'zl_borne_dt_fin_expos']
			for elem in champs : del self.fields[elem]

	def save(self, commit = True) :

		# Import
		from app.models import TCommune

		# Stockage des données du formulaire
		cleaned_data = self.cleaned_data
		val_comm = cleaned_data.get('zl_comm')
		val_dt_deb_expos = cleaned_data.get('zd_dt_deb_expos')
		val_dt_fin_expos = cleaned_data.get('zd_dt_fin_expos')
		val_dt_expos = cleaned_data.get('zd_dt_expos')
		val_borne_dt_deb_expos = cleaned_data.get('zl_borne_dt_deb_expos')
		val_borne_dt_fin_expos = cleaned_data.get('zl_borne_dt_fin_expos')
		val_borne_dt_expos = cleaned_data.get('zl_borne_dt_expos')
		val_rr = cleaned_data.get('zl_rr')

		# Initialisation de la valeur des attributs dt_expos et borne_dt_expos
		if val_dt_expos and val_borne_dt_expos :
			t = { 'dt_expos' : [val_dt_expos], 'borne_dt_expos' : [val_borne_dt_expos] }
		else :
			t = {
				'dt_expos' : [val_dt_deb_expos, val_dt_fin_expos],
				'borne_dt_expos' : [val_borne_dt_deb_expos, val_borne_dt_fin_expos]
			}

		# Création/modification d'une instance TExposition
		obj = super(GererExposition, self).save(commit = False)
		obj.borne_dt_expos = t['borne_dt_expos']
		obj.code_comm = TCommune.objects.get(pk = val_comm)
		obj.dt_expos = t['dt_expos']
		obj.id_reserv = self.kw_reserv
		obj.id_rr = val_rr
		obj.save()

		return obj