# coding: utf-8

# Import
from django import forms

class Authentifier(forms.Form) :
	
	# Champs
	zs_username = forms.CharField(label = 'Nom d\'utilisateur')
	zs_password = forms.CharField(label = 'Mot de passe', widget = forms.PasswordInput())

	def clean(self) :

		# Import
		from django.contrib.auth import authenticate

		# Stockage des données du formulaire
		cleaned_data = super(Authentifier, self).clean()
		val_username = cleaned_data.get('zs_username')
		val_password = cleaned_data.get('zs_password')

		# Vérification de l'état de l'identification
		if val_username and val_password and not authenticate(username = val_username, password = val_password) :
			self.add_error('__all__', 'Les identifiants rentrés sont incorrects.')

class GererUtilisateur(forms.ModelForm) :

	class Meta :

		# Import
		from app.models import TUtilisateur

		fields = ['email', 'first_name', 'last_name']
		model = TUtilisateur
		labels = {
			'email' : 'Courriel',
			'last_name' : 'Nom de famille'
		}

	def __init__(self, *args, **kwargs) :
		super(GererUtilisateur, self).__init__(*args, **kwargs)

		# Passage des champs à l'état requis
		self.fields['email'].required = True
		self.fields['first_name'].required = True
		self.fields['last_name'].required = True