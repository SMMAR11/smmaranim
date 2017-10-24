# coding: utf-8

# Import
from django.core.management.base import BaseCommand

class Command(BaseCommand) :

	# Imports
	from app.apps import AppConfig

	help = 'Initialisation de la base de données {}'.format(AppConfig.verbose_name)

	def handle(self, *args, **kwargs) :

		# Imports
		from app.apps import AppConfig
		from app.models import TClasse
		from app.models import TDroitsUtilisateur
		from app.models import TOrganisme
		from app.models import TStructure
		from app.models import TTypeIntervention
		from app.models import TTypePublic
		from app.models import TTypeUtilisateur
		from app.models import TUtilisateur
		from decouple import config
		from django.db import connection
		from smmaranim.custom_settings import CSV_ROOT
		import csv
		import os

		# Initialisation des données attributaires de chaque type d'utilisateur
		attrs_type_util = [
			{ 'pk' : 'A', 'int_type_util' : 'Administrateur' },
			{ 'pk' : 'PCDA', 'int_type_util' : 'Peut créer des animations' },
			{ 'pk' : 'PR', 'int_type_util' : 'Peut réserver' }
		]

		# Création des instances TTypeUtilisateur
		for attrs in attrs_type_util :
			if TTypeUtilisateur.objects.filter(pk = attrs['pk']).count() == 0 :
				TTypeUtilisateur.objects.create(**attrs)

		# Initialisation des données attributaires de l'organisme SMMAR
		attrs_org = { 'est_prest' : False, 'nom_org' : 'SMMAR' }

		# Création d'une instance TOrganisme
		if TOrganisme.objects.filter(nom_org = attrs_org['nom_org']).count() == 0 :
			TOrganisme.objects.create(**attrs_org)

		# Initialisation des données attributaires du compte utilisateur principal
		attrs_util = {
			'email' : config('MAIN_ACCOUNT_EMAIL'),
			'first_name' : config('MAIN_ACCOUNT_FIRSTNAME'),
			'id_org' : TOrganisme.objects.get(nom_org = attrs_org['nom_org']),
			'is_staff' :  True,
			'is_superuser' : True,
			'last_name' : config('MAIN_ACCOUNT_LASTNAME'),
			'username' : config('MAIN_ACCOUNT_USERNAME')
		}

		# Création du compte utilisateur principal (instance TUtilisateur)
		if TUtilisateur.objects.filter(username = attrs_util['username']).count() == 0 :
			obj_util = TUtilisateur(**attrs_util); obj_util.set_password('password'); obj_util.save()

			# Assignation de chaque type d'utilisateur
			for tu in TTypeUtilisateur.objects.all() :
				TDroitsUtilisateur.objects.create(code_type_util = tu, id_util = obj_util)

		# Initialisation des données attributaires de chaque type d'intervention
		attrs_type_interv = [
			{ 'pk' : 'AP', 'int_type_interv' : 'Animation ponctuelle'},
			{ 'pk' : 'PP', 'int_type_interv' : 'Programme pédagogique'}
		]

		# Création des instances TTypeIntervention
		for attrs in attrs_type_interv :
			if TTypeIntervention.objects.filter(pk = attrs['pk']).count() == 0 :
				TTypeIntervention.objects.create(**attrs)

		# Initialisation des données attributaires de chaque structure
		attrs_struct = [
			{ 'int_struct' : 'Autre', 'ordre_ld_struct' : 3 },
			{ 'int_struct' : 'Collectivité', 'ordre_ld_struct' : 2 },
			{ 'int_struct' : 'Établissement scolaire', 'ordre_ld_struct' : 1 }
		]

		# Création des instances TStructure
		for attrs in attrs_struct :
			if TStructure.objects.filter(int_struct = attrs['int_struct']).count() == 0 :
				TStructure.objects.create(**attrs)

		# Initialisation des données attributaires de chaque type de public
		attrs_type_public = [
			'Agriculteurs',
			'Élus',
			'Entreprises',
			'Handicapés',
			'Grand public',
			'Jeune public extra-scolaire',
			'Jeune public scolaire',
			'Personnes agées'
		]

		# Création des instances TTypePublic
		for attrs in attrs_type_public :
			if TTypePublic.objects.filter(int_type_public = attrs).count() == 0 :
				TTypePublic.objects.create(int_type_public = attrs)

		# Initialisation des données attributaires de chaque classe
		attrs_classe = [
			{ 'int_classe' : 'CE1', 'ordre_ld_classe' : 3 },
			{ 'int_classe' : 'CE2', 'ordre_ld_classe' : 4 },
			{ 'int_classe' : 'Cinquième', 'ordre_ld_classe' : 8 },
			{ 'int_classe' : 'CM1', 'ordre_ld_classe' : 5 },
			{ 'int_classe' : 'CM2', 'ordre_ld_classe' : 6 },
			{ 'int_classe' : 'CP', 'ordre_ld_classe' : 2 },
			{ 'int_classe' : 'Maternelle', 'ordre_ld_classe' : 1 },
			{ 'int_classe' : 'Post Bac', 'ordre_ld_classe' : 14 },
			{ 'int_classe' : 'Première', 'ordre_ld_classe' : 12 },
			{ 'int_classe' : 'Quatrième', 'ordre_ld_classe' : 9 },
			{ 'int_classe' : 'Seconde', 'ordre_ld_classe' : 11 },
			{ 'int_classe' : 'Sixième', 'ordre_ld_classe' : 7 },
			{ 'int_classe' : 'Terminale', 'ordre_ld_classe' : 13 },
			{ 'int_classe' : 'Troisième', 'ordre_ld_classe' : 10 }
		]

		# Création des instances TClasse
		for attrs in attrs_classe :
			if TClasse.objects.filter(int_classe = attrs['int_classe']).count() == 0 : TClasse.objects.create(**attrs)

		# Injection de données via des fichiers CSV
		for fichier in os.listdir(CSV_ROOT) :

			# Stockage du chemin du fichier CSV courant
			path = '{}/{}'.format(CSV_ROOT, fichier)

			# Ouverture du fichier CSV en lecture
			fichier_csv = open(path, 'r', encoding = 'cp1252')
			reader = csv.reader(fichier_csv, delimiter = ';')

			# Rédaction de la requête SQL
			sql = '''
			COPY {}({})
			FROM '{}'
			WITH DELIMITER ';'
			CSV HEADER
			ENCODING 'WIN1252';
			'''.format(fichier[:-4], ', '.join(next(reader)), path)
			
			# Exécution de la requête SQL
			with connection.cursor() as cursor :
				try :
					cursor.execute(sql)
				except :
					pass
			del cursor

		print('La base de données {} a été initialisée avec succès.'.format(AppConfig.verbose_name))