# coding: utf-8

'''
Mise en forme d'un gabarit normé pour chaque champ d'un formulaire
_form : Objet formulaire
Retourne un tableau associatif
'''
def sub(_form) :

	# Imports
	from bs4 import BeautifulSoup
	from django.template.defaultfilters import safe
	from smmaranim.custom_settings import ERROR_MESSAGES
	from smmaranim.custom_settings import MAY_BE_REQUIRED_FIELD
	from smmaranim.custom_settings import REQUIRED_FIELD

	output = {}

	# Mise en forme du gabarit par défaut
	gabarit_defaut = '''
	<div class="field-wrapper" id="fw_{}">
		<span class="field-label">{}</span>
		<span class="field">{}</span>
		<span class="field-error-message"></span>
	</div>
	'''

	for champ in _form :

		# Surchargement des messages d'erreur
		for cle, val in ERROR_MESSAGES.items() : _form.fields[champ.name].error_messages[cle] = val

		# Conversion du champ en code HTML (<=> chaîne de caractères)
		champ__str = BeautifulSoup('{}'.format(champ), 'html.parser')

		# Ajout d'une note à la fin du label de chaque champ obligatoire
		if champ.label :
			strs = champ.label.split('|')
			if _form.fields[champ.name].required == True :
				strs[0] += REQUIRED_FIELD
			else :
				for elem in champ__str.find_all() :
					if 'may-be-required' in elem.attrs.keys() : strs[0] += MAY_BE_REQUIRED_FIELD
			if champ.help_text : strs[0] += '<span class="help-icon" title="{}"></span>'.format(champ.help_text)
			champ.label = '|'.join(strs)

		# Définition de la valeur de l'attribut name
		attr_name = '{}-{}'.format(_form.prefix, champ.name) if _form.prefix else champ.name

		# Suppression de l'attribut required
		for elem in champ__str.find_all() :
			if 'may-be-required' in elem.attrs.keys() : del elem['may-be-required']
			if 'required' in elem.attrs.keys() : del elem['required']

		# Obtention du type de champ
		type_champ = champ.field.widget.__class__.__name__

		# Définition du gabarit
		if type_champ == 'CheckboxInput' :
			gabarit = '''
			<div class="field-wrapper" id="fw_{}">
				<span class="field">{}</span>
				<span class="field-label">{}</span>
				<span class="field-error-message"></span>
			</div>
			'''.format(attr_name, champ__str, champ.label)
		elif type_champ == 'ClearableFileInput' :

			# Stockage des inputs de type file et checkbox
			input_checkbox = champ__str.find('input', { 'type' : 'checkbox' })
			input_file = champ__str.find('input', { 'type' : 'file' })

			# Initialisation du bloc informations
			infos = ''
			for a in champ__str.find_all('a') :

				# Affichage de l'option "Effacer" si définie
				if input_checkbox :
					delete = '''
					<span class="delete-file">
						{}
						<label for="{}-clear_id">Effacer</label>
					</span>
					'''.format(input_checkbox, attr_name)
				else :
					delete = ''

				infos = '''
				<div class="if-return">
					<span class="file-infos">
						{}
					</span>
					{}
				</div>
				'''.format(a['href'], delete)

			gabarit = '''
				<div class="field-wrapper" id="fw_{}">
					<span class="field-label">{}</span>
					<div class="if-container">
						<span class="field">{}</span>
						<span class="if-trigger">Parcourir</span>
						{}
					</div>
					<span class="field-error-message"></span>
				</div>
				'''.format(attr_name, champ.label, input_file, infos)
		elif type_champ == 'DateInput' :
			gabarit = '''
			<div class="field-wrapper" id="fw_{}">
				<span class="field-label">{}</span>
				<div class="form-group">
					<span class="field">
						<div class="input-group">
							{}
							<span class="date input-group-addon" style="cursor: pointer;">
								<input name="{}__datepicker" type="hidden">
								<span class="glyphicon glyphicon-calendar"></span>
							</span>
						</div>
					</span>
				</div>
				<span class="field-error-message"></span>
			</div>
			'''.format(attr_name, champ.label, champ__str, attr_name)
		elif type_champ == 'DateTimeInput' :
			gabarit = gabarit_defaut.format(attr_name, champ.label, champ__str)
		elif type_champ == 'EmailInput' :

			# Obtention de la balise <input/> de type email
			champ__str = champ__str.find('input', { 'type' : 'email' })

			# Changement de type (email -> text)
			champ__str['type'] = 'text'

			gabarit = '''
			<div class="field-wrapper" id="fw_{}">
				<span class="field-label">{}</span>
				<div class="form-group">
					<span class="field">
						<div class="input-group">
							{}
							<span class="input-group-addon">
								<span class="fa fa-at"></span>
							</span>
						</div>
					</span>
				</div>
				<span class="field-error-message"></span>
			</div>
			'''.format(attr_name, champ.label, champ__str, attr_name)
		elif type_champ == 'NumberInput' :

			# Obtention de la balise <input/> de type number
			champ__str = champ__str.find('input', { 'type' : 'number' })

			# Changement de type (number -> text)
			champ__str['type'] = 'text'

			# Suppression d'attributs indésirables
			for ta in ['min'] :
				if champ__str.has_attr(ta) : del champ__str[ta]

			gabarit = gabarit_defaut.format(attr_name, champ.label, champ__str)
		elif type_champ == 'PasswordInput' :
			gabarit = gabarit_defaut.format(attr_name, champ.label, champ__str)
		elif type_champ == 'RadioSelect' :

			# Détermination du type de RadioSelect
			dtable = True
			for i in champ__str.find_all('input') :
				if not i.has_attr('into-datatable') : dtable = False

			# Détermination du gabarit
			if dtable == False :
				gabarit = gabarit_defaut.format(attr_name, champ.label, champ__str)
			else :

				# Stockage des labels
				labels = champ.label.split('|')

				# Initialisation des balises <tr/> de la balise <tbody/>
				trs = []
				for li in champ__str.find_all('li') :

					# Obtention de l'élément label (contient les données d'une balise <tr/>)
					label = li.find('label')

					# Obtention de l'élément input
					i = label.find('input')

					# Suppression de l'attribut into-datatable (inutile)
					del i['into-datatable']

					# Empilement des balises <tr/>
					if i['value'] :
						trs.append('<tr>{}</tr>'.format(
							''.join(['<td>{}</td>'.format(
								elem if elem != '__rb__' else i
							) for elem in label.text.split('|')])
						))

				gabarit = '''
				<div class="field-wrapper" id="fw_{}">
					<span class="field-label">{}</span>
					<div class="custom-table" id="dtable_{}">
						<table border="1" bordercolor="#DDD">
							<thead>
								<tr>{}</tr>
							</thead>
							<tbody>{}</tbody>
						</table>
					</div>
					<span class="field-error-message"></span>
				</div>
				'''.format(
					attr_name,
					labels[0],
					attr_name,
					''.join(['<th>{}</th>'.format(elem if elem != '__rb__' else '') for elem in labels[1:]]),
					''.join(trs)
				)

		elif type_champ == 'Select' :
			gabarit = gabarit_defaut.format(attr_name, champ.label, champ__str)
		elif type_champ == 'SelectMultiple' :

			# Stockage des labels
			labels = champ.label.split('|')

			# Initialisation des balises <tr/> de la balise <tbody/>
			trs = []
			for option in champ__str.find_all('option') :
				tds = []
				for index, elem in enumerate(option.text.split('|')) :
					td_content = elem
					if elem == '__zcc__' :
						kwargs = {
							'id' : 'id_{}_{}'.format(attr_name, index),
							'name' : attr_name,
							'type' : 'checkbox',
							'value' : option['value']
						} 
						if option.has_attr('selected') : kwargs['checked'] = True
						td_content = '<input {}>'.format(
							' '.join(['{}="{}"'.format(cle, val) for cle, val in kwargs.items()])
						)
					tds.append('<td>{}</td>'.format(td_content))
				trs.append('<tr>{}</tr>'.format(''.join(tds)))

			gabarit = '''
			<div class="field-wrapper" id="fw_{}">
				<span class="field-label">{}</span>
				<div class="custom-table" id="dtable_{}">
					<table border="1" bordercolor="#DDD">
						<thead>
							<tr>{}</tr>
						</thead>
						<tbody>{}</tbody>
					</table>
				</div>
				<span class="field-error-message"></span>
			</div>
			'''.format(
				attr_name,
				labels[0],
				attr_name,
				''.join(['<th>{}</th>'.format(
					elem if elem != '__zcc__' else '<input type="checkbox" id="id_{}__all" value="__ALL__">' \
					.format(attr_name)
				) for elem in labels[1:]]),
				''.join(trs)
			)
		elif type_champ == 'Textarea' :
			gabarit = gabarit_defaut.format(attr_name, champ.label, champ__str)
		elif type_champ == 'TextInput' :
			gabarit = gabarit_defaut.format(attr_name, champ.label, champ__str)
		elif type_champ == 'TimeInput' :
			gabarit = gabarit_defaut.format(attr_name, champ.label, champ__str)
		else :
			gabarit = None

		# Empilement du tableau des champs sauf si aucun gabarit disponible
		if gabarit :
			output[champ.name] = safe(gabarit)
		else :
			raise ValueError('Aucun gabarit n\'est disponible pour un champ {}.'.format(type_champ))

	return output