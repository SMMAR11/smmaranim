# coding: utf-8

# Import
from app.decorators import *

'''
Affichage du menu des raccourcis
_req : Objet requête
'''
@can_access('raccs')
def get_menu(_req) :

	# Imports
	from app.functions.menu_init import sub as menu_init
	from django.shortcuts import render

	output = None

	if _req.method == 'GET' :

		# Affichage du template
		output = render(_req, './menu.html', { 'menu' : menu_init(_req, 'raccs', 3), 'title' : 'Raccourcis' })

	return output