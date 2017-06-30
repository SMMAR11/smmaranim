# coding: utf-8

# Imports
from app.forms.admin import *
from app.models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

# Rafraîchissement des options
admin.site.disable_action('delete_selected')

class Organisme(admin.ModelAdmin) :

	def get_readonly_fields(self, _req, _obj = None) :
		if _obj : return self.readonly_fields + ('est_prest',)
		return self.readonly_fields

	actions = [admin.actions.delete_selected]
	fields = ['nom_org', 'est_prest', 'coul_org']
	list_display = ['nom_org']

admin.site.register(TOrganisme, Organisme)

class Outil(admin.ModelAdmin) :

	# Mise en forme des deux dernières colonnes
	def get_photo_outil__img(self, _obj) : return _obj.get_photo_outil__img({ 'height' : 40 })
	get_photo_outil__img.allow_tags = True
	get_photo_outil__img.short_description = 'Aperçu de l\'outil'

	actions = [admin.actions.delete_selected]
	fields = ['int_outil', 'descr_outil', 'photo_outil']
	list_display = ['int_outil', 'descr_outil', 'get_photo_outil__img']

	def save_model(self, _req, _obj, _form, _change) :

		# Tentative d'obtention d'une instance TOutil
		try :
			obj = TOutil.objects.get(pk = _obj.get_pk())
		except :
			obj = None

		# Suppression du fichier si modification
		if obj and 'photo_outil' in _form.changed_data : obj.get_photo_outil().delete()

		super(Outil, self).save_model(_req, _obj, _form, _change)

admin.site.register(TOutil, Outil)

class Utilisateur(UserAdmin) :

	def get_readonly_fields(self, _req, _obj = None) :
		if _obj : return self.readonly_fields + ('id_org',)
		return self.readonly_fields

	actions = [admin.actions.delete_selected]
	add_fieldsets = [
		['Données personnelles', { 'fields' : [('last_name'), ('first_name'), ('email')] }],
		['Données générales du compte', {
			'fields' : [('username'), ('zs_password'), ('zs_password_bis'), ('id_org')]
		}],
		['Options du compte', {
			'fields' : [('zl_type_util'), ('is_active'), ('is_staff'), ('is_superuser'), ('groups')]
		}]
	]
	add_form = FUtilisateurCreate
	fieldsets = [
		['Données personnelles', { 'fields' : [('last_name'), ('first_name'), ('email')] }],
		['Données générales du compte', { 'fields' : [('username'), ('password'), ('id_org')] }],
		['Options du compte', {
			'fields' : [('zl_type_util'), ('is_active'), ('is_staff'), ('is_superuser'), ('groups')]
		}]
	]
	form = FUtilisateurUpdate
	list_filter = []
	list_display = ['username', 'last_name', 'first_name', 'email', 'id_org', 'is_active', 'is_staff', 'is_superuser']

admin.site.register(TUtilisateur, Utilisateur)

# Retrait des fonctionnalités d'origine
admin.site.unregister(User)
#admin.site.unregister(Group)

class SousTypeIntervention(admin.ModelAdmin) :
	actions = [admin.actions.delete_selected]
	fields = list_display = ['int_sti', 'id_type_interv']

admin.site.register(TSousTypeIntervention, SousTypeIntervention)

class Commune(admin.ModelAdmin) :
	actions = [admin.actions.delete_selected]
	fields = list_display = ['code_comm', 'nom_comm']

admin.site.register(TCommune, Commune)

class Structure(admin.ModelAdmin) :
	actions = [admin.actions.delete_selected]
	fields = list_display = ['int_struct', 'ordre_ld_struct']

admin.site.register(TStructure, Structure)

class TypePublic(admin.ModelAdmin) :
	actions = [admin.actions.delete_selected]
	fields = list_display = ['int_type_public']

admin.site.register(TTypePublic, TypePublic)

class Ecole(admin.ModelAdmin) :
	actions = [admin.actions.delete_selected]
	fields = list_display = ['nom_ecole', 'code_comm']

admin.site.register(TEcole, Ecole)

class Classe(admin.ModelAdmin) :
	actions = [admin.actions.delete_selected]
	fields = list_display = ['int_classe', 'ordre_ld_classe']

admin.site.register(TClasse, Classe)

class Plaquette(admin.ModelAdmin) :

	# Mise en forme des deux dernières colonnes
	def get_plaq__a_img(self, _obj) : return _obj.get_plaq__a_img({ 'target' : 'blank' }, { 'height' : 40 })
	get_plaq__a_img.allow_tags = True
	get_plaq__a_img.short_description = 'Aperçu de l\'outil'

	actions = [admin.actions.delete_selected]
	fields = ['int_plaq', 'pdf_plaq', 'miniat_plaq']
	list_display = ['int_plaq', 'get_plaq__a_img']

	def save_model(self, _req, _obj, _form, _change) :

		# Tentative d'obtention d'une instance TPlaquette
		try :
			obj = TPlaquette.objects.get(pk = _obj.get_pk())
		except :
			obj = None

		# Suppression des fichiers si modification
		if obj :
			if 'miniat_plaq' in _form.changed_data : obj.get_miniat_plaq().delete()
			if 'pdf_plaq' in _form.changed_data : obj.get_pdf_plaq().delete()

		super(Plaquette, self).save_model(_req, _obj, _form, _change)

admin.site.register(TPlaquette, Plaquette)