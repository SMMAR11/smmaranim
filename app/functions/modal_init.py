# coding: utf-8

'''
Mise en forme d'une fenêtre modale
_suffix : Suffixe
_header : En-tête
_body : Contenu
Retourne une chaîne de caractères
'''
def sub(_suffix, _header, _body = '') :

	# Import
	from django.template.defaultfilters import safe

	modal = '''
	<div class="custom-modal fade modal" data-backdrop="static" data-keyboard="false" id="fm_{suffix}" role="dialog"
	tabindex="-1">
		<div class="modal-dialog">
			<div class="modal-content">
				<div class="modal-header">
					<button class="close" data-dismiss="modal" type="button">&times;</button>
					<span class="modal-title">{header}</span>
				</div>
				<div class="modal-body">
					<span id="za_fm_{suffix}" class="form-root">{body}</span>
					<div class="modal-padding-bottom"></div>
				</div>
			</div>
		</div>
	</div>
	'''.format(body = _body, header = _header, suffix = _suffix)

	return safe(modal)