# coding: utf-8

'''
Réinitialisation d'une datatable
_html : Code HTML
_datas : Données de sortie sous forme de tableau associatif
Retourne une réponse HTTP
'''
def sub(_html, _datas = {}) :

	# Imports
	from bs4 import BeautifulSoup
	from django.http import HttpResponse
	import json

	# Possibilité de manier le code HTML
	html = BeautifulSoup(_html)

	# Initialisation des données de sortie
	success = { cle : val for cle, val in _datas.items() }
	success['datatable'] = [[''.join(str(elem) for elem in td.contents if elem != '\n') for td in tr.find_all('td')] \
	for tr in html.find_all('tbody')[0].find_all('tr')]
	success['datatable_key'] = html.find_all('div', { 'class' : 'custom-table'})[0]['id'][7:]

	return HttpResponse(json.dumps({ 'success' : success }), content_type = 'application/json')