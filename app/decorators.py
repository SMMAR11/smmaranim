# coding: utf-8

'''
Vérification de l'accès à une vue
_mod : Clé du module
'''
def can_access(_mod = None) :
	def _method_wrapper(_vf) :
		def _args_wrapper(_req, *args, **kwargs) :

			# Imports
			from app.models import TUtilisateur
			from django.core.exceptions import PermissionDenied

			# Tentative d'obtention d'une instance TUtilisateur
			obj_util = TUtilisateur.get_util_connect(_req)

			# Jaugeage de l'éventualité d'une erreur 403
			erreur_403 = False
			if not obj_util :
				erreur_403 = True
			else :
				if _mod and _mod not in obj_util.get_menu() : erreur_403 = True

			# Exécution de la vue ou erreur 403
			if erreur_403 == False :
				return _vf(_req, *args, **kwargs)
			else :
				raise PermissionDenied

		return _args_wrapper
	return _method_wrapper