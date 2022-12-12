/**
 * Ajout d'une erreur de formulaire
 * _name : Nom du champ
 * _html : Message d'erreur
 */
function add_error(_name, _html) {

	// Ajout du message d'erreur
	$('#fw_' + _name).find('.field-error-message').append(
		$('<ul/>').append($('<li/>', { html : _html }))
	);

	// Ajout d'un style visuel
	$('#id_' + _name).addClass('invalid-field');
}

/**
 * Ajout d'un formulaire dans un formset
 * _suffix : Suffixe du formset
 */
function add_form_to_formset(_suffix) {

	// Stockage des objets source et cible
	var source = $('#formset_' + _suffix + '__empty_form').find('.formset-form');
	var cible = $('#formset_' + _suffix).find('#dtable_' + _suffix + ' tbody');

	// Clonage de l'objet source vers l'objet cible
	source.clone(true).appendTo(cible);

	// Réindexage des formulaires du formset
	reindex_formset('#formset_' + _suffix);
}

/**
 * Traitement(s) lié(s) à une requête AJAX
 * _e : Objet event
 */
function ajax(_e) {

	// Obtention d'un objet
	var obj = $(_e.target);

	// Définition du type de requête
	var req = (obj.attr('method') ? 'post' : 'get');

	// Pas de redirection automatique lors d'une requête POST (utilisation d'AJAX)
	if (req == 'post') {
		_e.preventDefault();
	}

	// Stockage de l'événement du DOM ainsi que les statuts possibles de celui-ci (afin d'éviter des requêtes AJAX
	// multiples)
	var dom_event = (req == 'post' ? 'onsubmit' : 'onclick');
	var dom_event_status = { 'off' : 'return false;', 'on' : obj.attr(dom_event) };

	// Stockage du suffixe de l'objet source
	var suffix = (req == 'post' ? obj.attr('name').substring(5) : obj.attr('modal-suffix'));

	// Exécution d'une requête AJAX
	var datas;
	$.ajax({
		beforeSend : function() {

			// Désactivation de l'événement du DOM
			obj.attr(dom_event, dom_event_status['off']);
		},
		complete : function() {

			// Nettoyage de l'erreur globale du formulaire
			$('#za_fge_' + suffix).remove();

			// Nettoyage des erreurs individuelles du formulaire
			if (req == 'post') {
				remove_errors(obj);
			}

			if (datas) {
				if (datas['success']) {

					// Traitement avec redirection non-brute
					if (datas['success']['redirect'] && datas['success']['message']) {

						// Nettoyage du contenu de la fenêtre modale cible
						$('#za_fm_' + suffix).empty();

						// Insertion du nouveau contenu de la fenêtre modale cible
						$('#za_fm_' + suffix).append(
							$('<div/>', { 'class' : 'valid-form', html : datas['success']['message'] })
						);

						// Affichage de la fenêtre modale cible (et suppression de la croix de fermeture)
						$('#fm_' + suffix).find('.close').remove();
						$('#fm_' + suffix).modal('show');

						// Redirection
						setTimeout(function() {
							if (datas['success']['redirect'] == '__RELOAD__') {
								window.location.reload();
							}
							else {
								window.location.href = datas['success']['redirect'];
							}
						}, 2000);
					}

					// Redirection brute
					if (datas['success']['redirect'] && !datas['success']['message']) {
						window.location.href = datas['success']['redirect'];
					}

					// Réinitialisation d'une datatable
					if (datas['success']['datatable'] && datas['success']['datatable_key']) {

						// Obtention de l'objet datatable
						var dtable = dtables[datas['success']['datatable_key']];

						// Nettoyage de la datatable
						dtable.clear().draw();

						for (var i = 0; i < datas['success']['datatable'].length; i += 1) {

							// Stockage des données
							var cols = datas['success']['datatable'][i];

							// Préparation d'une nouvelle ligne
							var lg = [];
							for (var j = 0; j < cols.length; j += 1) {
								lg.push(cols[j]);
							}

							// Ajout d'une ligne à la datatable
							dtable.row.add(lg).draw(true);
						}
					}

					// Affichage d'un contenu dans une fenêtre modale
					if (datas['success']['modal_content']) {
						$('#za_fm_' + suffix).html(datas['success']['modal_content']);
						$('#fm_' + suffix).modal('show');
					}

					// Évenement lié à une fenêtre modale (show ou hide)
					if (datas['success']['modal_status']) {
						$('#fm_' + suffix).modal(datas['success']['modal_status']);
					}

					// Réindexage des formulaires d'un formset
					if (datas['success']['reindex_formset'] && datas['success']['reindex_formset'] == true) {

						// Ajout d'une classe CSS indispensable
						$('#formset_' + suffix + ' tbody tr').each(function() {
							$(this).addClass('formset-form');
						});

						// Réindexage
						reindex_formset('#formset_' + suffix);
					}

					// Surchargement d'éléments
					if (datas['success']['elements']) {
						for (var i = 0; i < datas['success']['elements'].length; i += 1) {

							// Stockage de l'élément courant
							var elem = datas['success']['elements'][i];

							// Renommage de l'élément à supprimer
							var elem_to_remove = $(elem[0]).attr('id') + '__old';
							$(elem[0]).attr('id', elem_to_remove);

							// Insertion du nouvel élément
							$(elem[1]).insertAfter('#' + elem_to_remove);

							// Suppression de l'ancien élément
							$('#' + elem_to_remove).remove();
						}
					}

					// Clonage d'un formulaire
					if(datas['success']['clonings']) {

						// Réinitialisation de formsets
						if (datas['success']['reinit_formsets']) {
							for (var i = 0; i < datas['success']['reinit_formsets'].length; i += 1) {
								var elem = datas['success']['reinit_formsets'][i];

								// Suppression de tous les formulaires existants + réindexage
								$(elem[0]).find('.formset-form').remove();
								reindex_formset(elem[0]);

								// Ajout de X formulaires dans le formset afin de cloner des données à l'intérieur de
								// ceux-ci
								for (var j = 0; j < elem[1]; j += 1) {
									add_form_to_formset(elem[0].substr(9));
								}
							}
						}

						// Clonage
						for (var i = 0; i < datas['success']['clonings'].length; i += 1) {
							var elem = datas['success']['clonings'][i];
							if (elem['field_id'] && elem['field_value'] && elem['type']) {

								// Cas d'un champ texte
								if (elem['type'] == 'text') {
									$(elem['field_id']).val(elem['field_value']);
								}

								// Cas d'un champ bouton radio
								if (elem['type'] == 'radio') {
									$('input[name="' + elem['field_id'] + '"]').val([elem['field_value']]);
								}

								// Cas d'une case à cocher
								if (elem['type'] == 'checkbox') {
									for (var j = 0; j < elem['field_value'].length; j += 1) {
										var val = elem['field_value'][j];
										$('input[name="' + elem['field_id'] + '"][value="' + val + '"]').prop(
											'checked', true
										);
									}
								}
							}
						}
					}

					// Réinitialisation d'un formulaire
					if (datas['success']['reset'] && datas['success']['reset'] == true) {
						$('form[name="form_' + suffix + '"]')[0].reset();
					}
				}
				else {
					if (req == 'post') {
						var erreur_glob;
						for (var champ in datas) {
							if (champ.indexOf('__all__') > -1) {
								erreur_glob = datas[champ][0];
							}
							else {

								// Affichage du message d'erreur
								add_error(champ, datas[champ][0]);
							}
						}

						// Affichage du message d'erreur global si défini 
						if (erreur_glob) {
							obj.closest('.form-root').prepend($('<div/>', {
								'class' : 'form-global-error row', 'id' : 'za_fge_' + suffix, html : erreur_glob
							}));
						}
					}
				}
			}

			// Réactivation de l'événement du DOM
			obj.attr(dom_event, dom_event_status['on']);
		},
		contentType : false,
		data : (req == 'post' ? new FormData(obj.get(0)) : undefined),
		dataType : 'json',
		error : function(_xhr) {
			alert('Erreur ' + _xhr.status);
		},
		processData : false,
		success : function(_datas) {
			datas = _datas;	
		},
		type : req,
		url : obj.attr('action')
	});
}

/**
 * Initialisation d'une datatable
 * _id : Identifiant
 * _params : Paramètres sous forme de tableau associatif
 * Retourne un objet datatable
 */
function init_datatable(_id, _params = {}) {

	// Initialisation des paramètres
	var params = { 'autofit' : [], 'paging' : false, 'unbordered' : [], 'unsorting' : [] };
	for (cle in _params) {
		params[cle] = _params[cle];
	}

	// Ajustement dynamique de certaines colonnes
	$(_id + ' table th').each(function(_index) {
		if ($.inArray(_index, params['autofit']) > -1) {
			$(this).css({ 'width' : '1%' });
		}
	});

	return $(_id + ' table').DataTable({
		'aoColumnDefs' : [{
			'aTargets' : params['unsorting'], 'bSortable' : false
		}, {
			className : 'unbordered', 'targets' : params['unbordered']
		}],
		'autoWidth' : false,
		'info' : false,
		'language' : {
			'emptyTable' : 'Aucun enregistrement',
			'lengthMenu': 'Afficher _MENU_ enregistrements',
			'paginate' : { 'next' : 'Suivant', 'previous' : 'Précédent' }
		},
		'lengthMenu' : [[-1, 5, 10, 25, 50], ['---------', 5, 10, 25, 50]],
		'order' : [],
		'paging' : params['paging'],
		'searching' : false
	});
}

/**
 * Réindexage des formulaires d'un formset
 * _id : Identifiant du formset
 */
function reindex_formset(_id) {

	// Stockage des formulaires du formset
	var formsets = $(_id).find('.formset-form');

	for (var i = 0; i < formsets.length; i += 1) {
		$(formsets[i]).find('.field-wrapper').each(function() {

			// Obtention de la valeur de l'attribut name via l'élément field-wrapper
			var name = $(this).attr('id').replace(new RegExp('(\_\_prefix\_\_|\\d)'), i).substr(3);

			// Mise à jour de la valeur de l'attribut id de l'élément field-wrapper
			$(this).attr('id', 'fw_' + name);

			// Mise à jour de la valeur des attributs id et name liés au champ
			$(this).find('.field').children().attr({ 'id' : 'id_' + name, 'name' : name });
		});
	}

	// Mise à jour du nombre de formulaires constituant le formset
	$(_id).find('input[name$=TOTAL_FORMS]').val(parseInt(i));
}

/**
 * Suppression des erreurs individuelles d'un formulaire
 * _form : Objet formulaire
 */
function remove_errors(_form) {
	_form.find('.field-error-message').empty();
	_form.find('.invalid-field').removeClass('invalid-field');
}

/**
 * Suppression d'un formulaire d'un formset
 * _e : Objet event
 */
function remove_form_to_formset(_e) {

	// Obtention d'un élément DOM
	var obj = $(_e.target);

	// Stockage de l'identifiant du formset avant la suppression du formulaire lié
	var id = '#' + obj.parents('.formsets-wrapper').attr('id');

	// Suppression du formulaire lié
	obj.parents('.formset-form').remove();

	// Réindexage des formulaires du formset
	reindex_formset(id);
}