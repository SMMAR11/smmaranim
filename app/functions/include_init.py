# coding: utf-8

'''
Obtention d'une balise d'inclusion
_path : Chemin du fichier
Retourne une chaîne de caractères ou un objet NoneType
'''
def sub(_path) :

	# Import
	from django.conf import settings

	# Obtention de l'extension du fichier
	ext = _path.split('.')[-1]

	# Définition de la balise d'inclusion
	if ext == 'css' :
		output = '<link rel="stylesheet" type="text/css" href="{}{}">'.format(settings.STATIC_URL, _path)
	elif ext == 'js' :
		output = '<script type="text/javascript" src="{}{}"></script>'.format(settings.STATIC_URL, _path)
	else :
		output = None

	return output