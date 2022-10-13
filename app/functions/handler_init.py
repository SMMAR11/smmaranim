# coding: utf-8

'''
Définition d'un handler
_req : Objet requête
_sc : Code d'erreur
_mess : Message
Retourne une réponse HTTP
'''
def sub(_req, _sc, _mess) :

	# Imports
	from app.apps import AppConfig
	from app.functions.include_init import sub as include_init
	from django.shortcuts import render

	# Initialisation des fichiers d'inclusion
	includes = [
		'js/jquery.js',
		'vendors/bootstrap-3.3.7/css/bootstrap.css',
		'vendors/bootstrap-3.3.7/js/bootstrap.js',
		'vendors/font-awesome-4.7.0/css/font-awesome.min.css',
		'css/extensions/buttons.css',
		'css/extensions/fonts.css',
		'css/handler.css',
		'css/styles.css'
	]	

	# Affichage du template
	output = render(
		_req,
		'./handler.html',
		{
			'app_name' : AppConfig.verbose_name,
			'includes' : ''.join([include_init(elem) for elem in includes]),
			'message' : _mess,
			'title' : 'Erreur {}'.format(_sc)
		}
	)

	# Renseignement du code d'erreur
	output.status_code = _sc

	return output