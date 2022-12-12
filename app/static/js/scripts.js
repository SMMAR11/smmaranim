// Variable globale
var dtables = {};
var date_radiobuttons = ['AjouterExposition-rb_dt_expos', 'ModifierExposition-rb_dt_expos', 'rb_dt_reserv'];
var forms = [
	'chois_pm__gest_prep_real',
	'chois_pm__projet',
	'clon_bilan',
	'filtr_anim',
	'filtr_marche',
	'filtr_projet',
	'filtr_reserv'
];

/**
 * Affichage d'un loader dès la fin du chargement du DOM
 */
$(document).ready(function() {

	// Réinitialisation de chaque formulaire
	$('form').each(function() {
		$(this)[0].reset();
	});

	// Désaffichage de la page web (leurre)
	$('.container-fluid').hide();
	$('body').css({ 'background-color' : '#FFF', 'margin-bottom' : 0 });

	// Stockage du contenu du loader
	var contenu = [
		$('<span/>', { 'class' : 'fa fa-circle-o-notch fa-spin' }),
		$('<br/>'),
		'Chargement de la page'
	];

	// Préparation du loader (centrage vertical)
	var divs = [$('<div/>', { 'id' : 'main-loader' }), $('<div/>')];
	for (var i = 0; i < contenu.length; i += 1) {
		divs[1].append(contenu[i]);
	}
	divs[1].appendTo(divs[0]);

	// Affichage du loader
	divs[0].prependTo('body');
});

/**
 * Désaffichage du loader dès la fin du chargement d'une page web
 */
$(window).on('load', function() {
	setTimeout(function() {

		// Initialisation des datatables
		dtables = {
			'aides' : init_datatable('#dtable_aides'),
			'alert' : init_datatable('#dtable_alert', { 'autofit' : [0], 'unsorting' : '_all' }),
			'anims' : init_datatable('#dtable_anims', { 'autofit' : [5], 'unsorting' : [5] }),
			'chois_marche' : init_datatable('#dtable_chois_marche', { 'autofit' : [4], 'unsorting' : [1, 2, 4] }),
			'chois_projet' : init_datatable('#dtable_chois_projet', { 'autofit' : [5], 'unsorting' : [5] }),
			'consult_cep' : init_datatable('#dtable_consult_cep'),
			'consult_cont_refer' : init_datatable(
				'#dtable_consult_cont_refer', { 'autofit' : [4, 5], 'unbordered' : [4, 5], 'unsorting' : [4, 5] }
			),
			'consult_expos' : init_datatable(
				'#dtable_consult_expos', { 'autofit' : [4, 5, 6], 'unbordered' : [4, 5, 6], 'unsorting' : [4, 5, 6] }
			),
			'consult_pm' : init_datatable(
				'#dtable_consult_pm', { 'autofit' : [10], 'unsorting' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] }
			),
			'consult_projet' : init_datatable('#dtable_consult_projet', { 'autofit' : [5], 'unsorting' : [5] }),
			'consult_ta' : init_datatable('#dtable_consult_ta'),
			'consult_tdj' : init_datatable('#dtable_consult_tdj', { 'unsorting' : [2, 3] }),
			'ger_cep' : init_datatable('#dtable_ger_cep', { 'autofit' : [2], 'unsorting' : '_all' }),
			'ger_point' : init_datatable('#dtable_ger_point', { 'autofit' : [3], 'unsorting' : '_all' }),
			'ger_ta' : init_datatable('#dtable_ger_ta', { 'autofit' : [3], 'unsorting' : '_all' }),
			'ger_tdj' : init_datatable('#dtable_ger_tdj', { 'autofit' : [3], 'unsorting' : '_all' }),
			'plaq' : init_datatable('#dtable_plaq', { 'autofit' : [0], 'unsorting' : [0] }),
			'point' : init_datatable('#dtable_point'),
			'prest' : init_datatable('#dtable_prest', {
				'autofit' : [2, 3, 4],
				'unbordered' : [10, 11, 12],
				'unsorting' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
			}),
			'prest2' : init_datatable('#dtable_prest2', {
				'autofit' : [2, 3],
				'unbordered' : [5, 6],
				'unsorting' : [5, 6]
			}),
			'zcc_plaq' : init_datatable('#dtable_zcc_plaq', { 'autofit' : [0, 2], 'paging' : true, 'unsorting' : '_all' }),
			'zl_outil' : init_datatable('#dtable_zl_outil', { 'autofit' : [0, 3], 'paging' : true, 'unsorting' : '_all' }),
			'real_etats_Bilan_Animations_Facturation' : init_datatable(
				'#dtable_real_etats_Bilan_Animations_Facturation', {
					'autofit': [7],
					'unsorting': [7]
				}
			)
		};

		// Suppression du loader
		$('#main-loader').remove();

		// Affichage de la page web
		$('body').removeAttr('style');
		$('.container-fluid').show();
	}, 250);
});

/**
 * Initialisation d'éléments du DOM
 */
$(document).on('mousemove', function() {

	// Mise en place d'un calendrier sur chaque champ date
	$('.date').datepicker({
		autoclose : true,
		endDate : '31/12/2999',
		keyboardNavigation : false,
		language : 'fr',
		maxViewMode : 2,
		orientation : 'bottom right',
		startDate : '01/01/2000'
	});
});

/**
 * Affichage de la valeur choisie via un datepicker
 */
$(document).on('change', 'input[name$="__datepicker"]', function() {

	// Stockage et transfert de la valeur cachée
	var attr_name = $(this).attr('name');
	$('#id_' + attr_name.substr(0, attr_name.length - 12)).val($(this).val());
});

/**
 * Affichage d'un loader avant le lancement d'une requête AJAX
 */
$(document).ajaxSend(function() {

	// Initialisation du loader et de son contenu
	var loader = $('<div/>', { 'class' : 'text-center', 'id' : 'ajax-loader' });
	var contenu = [
		$('<span/>', { 'class' : 'fa fa-circle-o-notch fa-spin' }),
		$('<br/>'),
		'Veuillez patienter...'
	];

	// Préparation du loader
	for (var i = 0; i < contenu.length; i += 1) {
		loader.append(contenu[i]);
	}

	// Affichage du loader
	loader.insertAfter('.container-fluid');
});

/**
 * Désaffichage d'un loader dès la fin d'une requête AJAX
 */
$(document).ajaxComplete(function() {
	$('#ajax-loader').remove();
});

/**
 * Soumission de formulaires lors de l'appel d'un événement onchange
 */
for (var i = 0; i < forms.length; i += 1) {
	$('form[name="form_' + forms[i] + '"]').on('change', function() {
		$(this).submit();
	});
}

/**
 * Gestion d'affichage des champs date
 */
for (var i = 0; i < date_radiobuttons.length; i += 1) {
	$(document).on('change', 'input[name="' + date_radiobuttons[i] + '"]', function() {

		// Stockage du nom de l'élément bouton radio
		var elem = $(this).attr('name');

		/**
		 * Affichage ou désaffichage d'un bloc date
		 * _suffix : Suffix du bloc
		 * _action : hide ou show
		 */
		function hide_or_show(_suffix, _action) {

			// Définition du bloc à gérer
			var split = elem.split('-');
			var name = split.slice(-1).join('').substr(3);
			if (split.length > 1) {
				name = split[0] + '-' + name;
			}
			var id = '#za_' + name + '__' + _suffix;
			
			if (_action == 'show') {
				$(id).show();
			}
			else {
				$(id).hide();
			}
		}

		if ($(this).val() == 1) {
			hide_or_show('on', 'hide');
			hide_or_show('off', 'show');
		}
		else {
			hide_or_show('off', 'hide');
			hide_or_show('on', 'show');
		}
	});
}

/**
 * Obtention du nom d'un fichier uploadé
 */
$(document).on('change', 'input[type="file"]', function() {

	// Obtention d'un élément "field-wrapper"
	var fw = $('#fw_' + $(this).attr('name'));

	// Retrait du nom de l'ancien fichier uploadé
	fw.find('.if-return').remove();

	// Préparation du nom du nouveau fichier uploadé
	var div = $('<div/>', { 'class' : 'if-return' });
	var span = $('<span/>', { 'class' : 'file-infos', html : ' ' + $(this).val() });

	// Affichage du nom du nouveau fichier uploadé
	div.append(span);
	div.insertAfter(fw.find('.if-trigger'));

	// Application d'un style CSS.
	fw.find('.if-trigger').css('margin-right', '3.5px');
});

/**
 * Cochage/décochage automatique d'un groupe de cases à cocher
 */
$('input[type="checkbox"]').on('change', function() {

	// Obtention d'un objet case à cocher
	var obj = $(this);

	if (obj.val() == '__ALL__') {

		// Stockage du nom du groupe de cases à cocher
		var get_name = obj.attr('id').substr(3);
		get_name = get_name.substr(0, get_name.length - 5);

		$('input[name="' + get_name + '"]').each(function() {
			if (obj.is(':checked')) {
				this.checked = true;
			}
			else {
				this.checked = false;
			}
		});
	}
	else {

		// Décochage de la case à cocher permettant le cochage/décochage automatique d'un groupe de cases à cocher
		if (obj.is(':checked') == false) {
			$('#id_' + obj.attr('name') + '__all').prop('checked', false);
		}
	}
});

/**
 * Edition du bilan des animations justificatif de facturation
 */
$('#bt_editBilan_Animations_Facturation').on('click', function() {
	$('form[name="form_real_etats_Bilan_Animations_Facturation"').attr('action', '?action=editer-bilan');
	$('form[name="form_real_etats_Bilan_Animations_Facturation"').submit();
	$('form[name="form_real_etats_Bilan_Animations_Facturation"').attr('action', '');
});