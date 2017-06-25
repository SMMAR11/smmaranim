# coding: utf-8

'''
Obtention d'une rangée de dates avec les bornes associées
_array : Tableau associatif à deux clés (dates et bounds)
Retourne un tableau
'''
def sub(_array) :
	
	# Import
	from datetime import timedelta

	output = []

	# Initialisation d'une rangée de dates
	dates = [_array['dates'][0] + timedelta(elem) for elem in range(
		(_array['dates'][-1] - _array['dates'][0]).days + 1
	)]

	# Initialisation de la sortie
	for d in dates :
		if d == _array['dates'][0] :
			bound = _array['bounds'][0]
		elif d == _array['dates'][-1] :
			bound = _array['bounds'][-1]
		else :
			bound = 'WD'
		output.append([d, bound])

	return output