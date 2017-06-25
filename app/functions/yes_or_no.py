# coding: utf-8

'''
Affichage d'une demande de suppression
_action : Valeur de l'attribut action
_suffix : Suffixe
_datas : Données pouvant être supprimées en cascade et constitutrices d'un message d'avertissement
Retourne une chaîne de caractères
'''
def sub(_action, _suffix, _datas = []) :

	# Tri du tableau des données par intitulé
	datas = list(sorted(_datas, key = lambda l : l[0]))

	# Définition du message d'avertissement
	message = '''
	<span class="important">
		Attention, les éléments suivants seront également supprimés :
		<ul class="list-inline">{}</ul>
	</span>
	'''.format(''.join(['<li>{}</li>'.format('{} : {}'.format(*elem)) for elem in datas if elem[1] > 0]))

	# Détermination de l'affichage du message d'avertissement
	alerte = False
	for elem in datas :
		if elem[1] > 0 : alerte = True

	return '''
	{}
	<div class="row">
		<div class="col-xs-6">
			<button action="{}" class="center-block custom-button main-button" modal-suffix="{}"
			onclick="ajax(event);">
				Oui
			</button>
		</div>
		<div class="col-xs-6">
			<button class="center-block custom-button main-button" data-dismiss="modal">Non</button>
		</div>
	</div>
	'''.format(message if alerte == True else '', _action, _suffix)