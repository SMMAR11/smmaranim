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