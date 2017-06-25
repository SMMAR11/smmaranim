# coding: utf-8

'''
Obtention d'un gabarit normé pour chaque attribut
_attrs : Attributs sous forme d'un tableau associatif
Retourne un tableau associatif
'''
def sub(_attrs, _pdf = False) :

	# Import
	from django.template.defaultfilters import safe

	output = {}

	for cle, val in _attrs.items() :
		if 'label' in val and 'value' in val :

			# Stockage du label et de la valeur attributaire
			label = val['label'] or ''
			value = val['value'] if val['value'] else val['null'] if 'null' in val else '' if _pdf == False else '-'

			# Définition du contenu de l'attribut
			attr_content = None
			if 'table' in val :
				if val['table'] == True and 'table_header' in val :

					# Initialisation des lignes de la balise <thead/>
					trs = []

					for tr in val['table_header'] :

						# Initialisation des colonnes de la balise <tr/>
						ths = []

						for th in tr :

							# Initialisation des attributs de la balise <th/>
							th_attrs = ['{}="{}"'.format(*ta.split(':')) for ta in th[1].split('|')] if th[1] else []

							# Empilement des colonnes de la balise <tr/>
							ths.append('<th {}>{}</th>'.format(' '.join(th_attrs), th[0]))

						# Empilement des lignes de la balise <thead/>
						trs.append('<tr>{}</tr>'.format(''.join(ths)))

					# Défintion du contenu des balises <thead/> et <tbody/>
					thead = ''.join(trs)
					tbody = ''.join(
						['<tr>{}</tr>'.format(''.join(['<td>{}</td>'.format(td) for td in tr])) for tr in value]
					)

					if _pdf == False :
						attr_content = '''
						<span class="attribute-label">{}</span>
						<div class="custom-table" id="dtable_{}">
							<table border="1" bordercolor="#DDD">
								<thead>{}</thead>
								<tbody>{}</tbody>
							</table>
						</div>
						'''.format(label, cle, thead, tbody)
					else :
						attr_content = '''
						<span class="pdf-attribute-label">{}</span>
						<table border="1" bordercolor="#DDD" class="pdf-table">
							<thead>{}</thead>
							<tbody>{}</tbody>
						</table>
						'''.format(label, thead, tbody if not tbody == '<tr><td>-</td></tr>' else '')
			else :
				attr_content = '''
				<span class="{pdf}attribute-label">{label}</span>
				<div class="{pdf}attribute">{value}</div>
				'''.format(label = label, pdf = 'pdf-' if _pdf == True else '', value = value)

			# Empilement du tableau des attributs si un contenu a été défini
			if attr_content :
				output[cle] = safe('<div class="{pdf}attribute-wrapper">{content}</div>'.format(
					content = attr_content, pdf = 'pdf-' if _pdf == True else ''
				))

	return output