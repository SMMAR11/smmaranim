# coding: utf-8

# Imports
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View

@method_decorator(login_required, name='dispatch')
class Bilan_Animations_Facturation(View):

	# Imports
	from app.forms.real_etats.Bilan_Animations_Facturation import Bilan_Animations_Facturation as fBAF

	# Options Django
	form_class = fBAF
	template_name = './real_etats/template.html'

	# Méthodes Django

	def get(self, rq, *args, **kwargs):

		# Imports
		from django.shortcuts import render

		# Initialisation du formulaire
		form = self.form_class(kwarg_rq=rq)

		# Edition du bilan des animations justificatif de facturation
		if rq.GET.get('action') == 'editer-bilan':
			return form.edit_bilan()

		# Affichage de la page web
		else:
			return render(rq, self.template_name, {
				'datatable': form.get_datatable(),
				'extra': '''
				<br>
				<span
					class="icon-with-text word-icon"
					id="bt_editBilan_Animations_Facturation"
				>Éditer le bilan des animations justificatif de facturation</span>
				''',
				'form': form.get_form(),
				'title': 'Bilan des animations justificatif de facturation'
			})

	def post(self, rq, *args, **kwargs):

		# Imports
		from app.functions.datatable_reset import sub as datatable_reset
		from django.http import HttpResponse
		from django.urls import reverse
		import json

		# Soumission du formulaire
		form = self.form_class(rq.POST, kwarg_rq=rq)

		# Si le formulaire est valide, alors...
		if form.is_valid():

			# Si édition du bilan, alors...
			if rq.GET.get('action') == 'editer-bilan':

				# Paramètres GET de l'URL après actualisation
				cleanedData = form.cleaned_data
				getParameters = {
					'action': 'editer-bilan',
					'marcheLot': cleanedData['zl_marche_lot'],
					'marcheLotBilanPeriodeDu': cleanedData['zd_date_debut'],
					'marcheLotBilanPeriodeAu': cleanedData['zd_date_fin']
				}

				# URL après actualisation
				redirect = '?'.join([
					reverse('bilan_animations_facturation'),
					'&'.join('='.join(i) for i in [
						[k, str(v)] for k, v in getParameters.items()
					])
				])

				# Actualisation de la vue
				return HttpResponse(
					json.dumps({'success': {'redirect': redirect}}),
					content_type = 'application/json'
				)

			# Rafraîchissement de la datatable
			return datatable_reset(form.get_datatable())

		# Sinon, affichage des erreurs
		else:
			return HttpResponse(
				json.dumps(form.errors), content_type='application/json'
			)

		return None