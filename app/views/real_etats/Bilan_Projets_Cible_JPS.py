# coding: utf-8

# Imports
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View

@method_decorator(login_required, name='dispatch')
class Bilan_Projets_Cible_JPS(View):

	# Imports
	from app.forms.real_etats.Bilan_Projets_Cible_JPS import Bilan_Projets_Cible_JPS as fBPJPS

	# Options Django
	form_class = fBPJPS
	template_name = './real_etats/template.html'

	# Méthodes Django

	def get(self, rq, *args, **kwargs):

		# Imports
		from django.shortcuts import render

		# Initialisation du formulaire
		form = self.form_class(kwarg_rq=rq)

		# Affichage de la page web
		return render(rq, self.template_name, {
			'datatable': form.get_datatable(),
			'form': form.get_form(),
			'title': 'Bilan des projets visant le jeune public scolaire'
		})

	def post(self, rq, *args, **kwargs):

		# Imports
		from app.functions.datatable_reset import sub as datatable_reset
		from django.http import HttpResponse
		import json

		# Soumission du formulaire
		form = self.form_class(rq.POST, kwarg_rq=rq)

		# Si le formulaire est valide, alors rafraîchissement de la
		# datatable
		if form.is_valid():
			return datatable_reset(form.get_datatable())

		# Sinon, affichage des erreurs
		else:
			return HttpResponse(
				json.dumps(form.errors),
				content_type='application/json'
			)