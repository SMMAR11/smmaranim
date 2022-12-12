# coding: utf-8

# Import
from app.decorators import *

'''
Affichage du menu des bilans
_req : Objet requête
'''
@can_access('real_etats')
def get_menu(_req) :

	# Imports
	from app.functions.menu_init import sub as menu_init
	from django.shortcuts import render

	output = None

	if _req.method == 'GET' :

		# Affichage du template
		output = render(_req, './menu.html', {
			'menu' : menu_init(_req, 'real_etats', 2),
			'title' : 'Bilans'
		})

	return output