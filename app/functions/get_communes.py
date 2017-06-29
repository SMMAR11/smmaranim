# coding: utf-8

'''
Obtention d'une liste de communes classée par départements
Retourne un tableau associatif
'''
def sub() :

	# Imports
	from app.models import TCommune
	from smmaranim.custom_settings import DEPARTMENTS

	output = []

	# Initialisation des communes
	communes = [[c.get_pk(), c] for c in TCommune.objects.order_by('nom_comm')]

	# Initialisation des communes par département
	departs = sorted([[j for j in communes if j[0][:2] == i] for i in set(map(lambda l : l[0][:2], communes))])

	# Initialisation des choix de la liste déroulante des communes
	for d in departs :

		# Stockage du numéro du département
		num = d[0][0][:2]

		# Empilement des choix de la liste déroulante des communes par filtrage par rapport au numéro de département
		if num in DEPARTMENTS.keys() : output.append([DEPARTMENTS[num], [c for c in d]])

	return output