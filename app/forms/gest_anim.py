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
		if 'A' not in self.kw_util.get_type_util__list() : self.fields['zl_org'].empty_label = None

	def get_calendar(self, _req, *args, **kwargs) :

		# Imports
		from datetime import date
		from smmaranim.custom_settings import MONTHS
		import calendar

		# Stockage des données du formulaire
		if _req.method == 'GET' :
			val_outil = self.fields['zl_org'].initial
			val_mois = self.fields['zl_mois'].initial
			val_annee = self.fields['zl_annee'].initial
		else :
			cleaned_data = self.cleaned_data
			val_outil = cleaned_data.get('zl_org')
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

					td = '''
					<td class="mc-day">
						<span class="mcd-label">{}</span>
						{}
					</td>
					'''.format(quant, '')

					# Incrémentation du quantième
					quant += 1

				else :
					td = '<td></td>'
					
				tds.append(td)
			trs.append('<tr>{}</tr>'.format(''.join(tds)))

		return '''
		<div id="za_cal_anim">
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