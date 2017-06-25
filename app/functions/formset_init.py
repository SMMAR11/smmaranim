# coding: utf-8

'''
Mise en forme d'un formset
_suffix : Suffixe
_form : Objet formulaire
_formset_label : Tableau associatif (label du formset + le champ est-il requis ?)
_keys : Ordre d'affichage de chaque champ
_kwargs : Arguments sous forme de tableau associatif
Retourne un tableau
'''
def sub(_suffix, _form, _formset_label, _keys, _kwargs = {}) :

	# Imports
	from app.functions.form_init import sub as form_init
	from bs4 import BeautifulSoup
	from django.forms import formset_factory
	from django.template.defaultfilters import safe
	from smmaranim.custom_settings import REQUIRED_FIELD

	# Initialisation des arguments
	kwargs = { 'formset' : None, 'initial' : None }
	for cle, val in _kwargs.items() : kwargs[cle] = val

	# Initialisation du formset et de ses arguments
	formset_kwargs = { 'extra' : 1 if not kwargs['initial'] else 0 }
	if kwargs['formset'] : formset_kwargs['formset'] = kwargs['formset']
	F = formset_factory(_form, **formset_kwargs)
	formset = F(initial = kwargs['initial'])

	# Initialisation des lignes de la datatable
	trs = []

	for form in formset :

		# Initialisation des balises <th/> et <td/>
		ths = []
		tds = []

		# Initialisation de chaque champ du formulaire courant
		form = form_init(form)

		for key in _keys.split('|') :

			# Instanciation d'un objet BeautifulSoup
			bs = BeautifulSoup(form[key])

			# Obtention du label original
			label = bs.find('span', { 'class' : 'field-label'})

			# Empilement des balises <th/>
			ths.append('<th>{}</th>'.format(''.join(str(elem) for elem in label.contents)))
			
			# Suppression du label (surchargement avec une chaîne vide)
			label.replaceWith('')

			# Empilement des balises <td/>
			tds.append('<td>{}</td>'.format(bs))

		# Ajout d'une colonne permettant la gestion du formset
		ths.append(
			'''
			<th>
				<span class="add-form fa fa-plus-circle" onclick="add_form_to_formset('{}');" title="Ajouter"></span>
			</th>
			'''.format(_suffix)
		)
		tds.append(
			'''
			<td><span class="delete-icon icon-without-text" onclick="remove_form_to_formset(event);"
			title="Supprimer"></span></td>
			'''
		)

		# Empilement des lignes de la datatable
		trs.append('<tr class="formset-form">{}</tr>'.format(''.join(tds)))

	# Initialisation des balises <td/> du formulaire vide
	tds = []

	# Initialisation de chaque champ du formulaire vide
	empty_form = form_init(formset.empty_form)

	for key in _keys.split('|') :

		# Instanciation d'un objet BeautifulSoup
		bs = BeautifulSoup(empty_form[key])
			
		# Suppression du label (surchargement avec une chaîne vide)
		bs.find('span', { 'class' : 'field-label'}).replaceWith('')

		# Empilement des balises <td/> du formulaire vide
		tds.append('<td>{}</td>'.format(bs))

	# Ajout d'une colonne permettant la gestion du formset
	tds.append(
		'''
		<td><span class="delete-icon icon-without-text" onclick="remove_form_to_formset(event);"
		title="Supprimer"></span></td>
		'''
	)

	output = [
		'''
		<div id="formset_{}" class="formsets-wrapper">
			{}
			<span class="formset-label">{}</span>
			<div class="custom-table" id="dtable_{}">
				<table border="1" bordercolor="#DDD">
					<thead>
						<tr>{}</tr>
					</thead>
					<tbody>{}</tbody>
				</table>		
			</div>
		</div>
		'''.format(
			_suffix,
			formset.management_form,
			_formset_label[0] + REQUIRED_FIELD if _formset_label[1] == True else _formset_label[0],
			_suffix,
			''.join(ths),
			''.join(trs)
		),
		'''
		<div id="formset_{}__empty_form" style="display: none;">
			<form>
				<table>
					<tbody>
						<tr class="formset-form">{}</tr>
					</tbody>
				</table>
			</form>
		</div>
		'''.format(_suffix, ''.join(tds))
	]

	return [safe(elem) for elem in output]