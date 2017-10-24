# coding: utf-8

# Imports
from app.models import TOrganisme
from decouple import config
from django.conf import settings
import os

ALERTS = {
	'aides_smmar' : '''
	Attention, le SMMAR se réserve le droit de ne pas exécuter les actions souhaitées par le demandeur.
	'''
}

CSV_ROOT = os.path.join(settings.BASE_DIR, 'csv')

DEPARTMENTS = { '09' : 'Ariège', '11' : 'Aude', '34' : 'Hérault', '66' : 'Pyrénées-Orientales', '81' : 'Tarn' }

EMPTY_VALUE = (u'', '---------')

ERROR_MESSAGES = {
    'invalid' : 'Veuillez renseigner une valeur valide.',
    'invalid_choice' : 'Veuillez renseigner une valeur valide.',
    'email_or_phone_number' : 'Veuillez renseigner une adresse électronique et/ou un numéro de téléphone valide(s).',
    'required' : 'Veuillez renseigner une valeur.'
}

EVALUATION_CHOICES = ['TOP', 'BOF', 'FLOP']

HALF_DAY_CHOICES = [0.5, 1, 2]

INCLUDE_FILES = {
	'head' : [
		'js/jquery.js',
		'vendors/bootstrap-3.3.7/css/bootstrap.css',
		'vendors/bootstrap-3.3.7/js/bootstrap.js',
		'vendors/font-awesome-4.7.0/css/font-awesome.min.css',
		'vendors/DataTables/css/jquery.dataTables.css',
		'vendors/DataTables/js/jquery.dataTables.js',
		'vendors/bootstrap-datepicker-1.6.4/css/bootstrap-datepicker.min.css',
		'vendors/bootstrap-datepicker-1.6.4/js/bootstrap-datepicker.min.js',
		'vendors/bootstrap-datepicker-1.6.4/locales/bootstrap-datepicker.custom-fr.js',
		'css/template.css',
		'css/extensions/buttons.css',
		'css/extensions/controls.css',
		'css/extensions/datatables.css',
		'css/extensions/datepickers.css',
		'css/extensions/forms.css',
		'css/extensions/formsets.css',
		'css/extensions/modals.css',
		'css/extensions/panels.css',
		'css/extensions/tabs.css',
		'css/extensions/thumbnails.css',
		'css/extensions/wells.css',
		'css/styles.css'
	],
	'body' : [
		'js/functions.js',
		'js/scripts.js'
	]
}

MAX_SIZE = 5

MAY_BE_REQUIRED_FIELD = '<span class="may-be-required-field"></span>'

MENU = {
	'gest_anim' : {
		'mod_img' : settings.STATIC_URL + 'images/thumbnails/gest_anim/main.png',
		'mod_items' : {
			'ajout_anim' : {
				'item_img' : settings.STATIC_URL + 'images/thumbnails/gest_anim/ajout_anim.png',
				'item_name' : 'Ajouter une animation',
				'item_rank' : 1,
				'item_url_name' : 'ajout_anim'
			},
			'consult_reserv' : {
				'item_img' : settings.STATIC_URL + 'images/thumbnails/gest_anim/consult_anim.png',
				'item_name' : 'Consulter une animation',
				'item_rank' : 2,
				'item_url_name' : 'chois_anim'
			}
		},
		'mod_name' : 'Gestion des animations',
		'mod_rank' : 3,
		'mod_rights' : ['A', 'PCDA'],
		'mod_url_name' : 'gest_anim'
	},
	'gest_projets' : {
		'mod_img' : settings.STATIC_URL + 'images/thumbnails/gest_projets/main.png',
		'mod_items' : {
			'ajout_projet' : {
				'item_img' : settings.STATIC_URL + 'images/thumbnails/gest_projets/ajout_projet.png',
				'item_name' : 'Ajouter un projet',
				'item_rank' : 1,
				'item_url_name' : 'ajout_projet'
			},
			'consult_projet' : {
				'item_img' : settings.STATIC_URL + 'images/thumbnails/gest_projets/consult_projet.png',
				'item_name' : 'Consulter un projet',
				'item_rank' : 2,
				'item_url_name' : 'chois_projet'
			}
		},
		'mod_name' : 'Gestion des projets',
		'mod_rank' : 2,
		'mod_rights' : ['A', 'PCDA'],
		'mod_url_name' : 'gest_projets'
	},
	'gest_marches' : {
		'mod_img' : settings.STATIC_URL + 'images/thumbnails/gest_marches/main.png',
		'mod_items' : {
			'ajout_marche' : {
				'item_img' : settings.STATIC_URL + 'images/thumbnails/gest_marches/ajout_marche.png',
				'item_name' : 'Ajouter un marché',
				'item_rank' : 1,
				'item_url_name' : 'ajout_marche'
			},
			'consult_marche' : {
				'item_img' : settings.STATIC_URL + 'images/thumbnails/gest_marches/consult_marche.png',
				'item_name' : 'Consulter un marché',
				'item_rank' : 2,
				'item_url_name' : 'chois_marche'
			}
		},
		'mod_name' : 'Gestion des marchés',
		'mod_rank' : 1,
		'mod_rights' : ['A'],
		'mod_url_name' : 'gest_marches'
	},
	'gest_reserv' : {
		'mod_img' : settings.STATIC_URL + 'images/thumbnails/gest_reserv/main.png',
		'mod_items' : {
			'ajout_reserv' : {
				'item_img' : settings.STATIC_URL + 'images/thumbnails/gest_reserv/ajout_reserv.png',
				'item_name' : 'Ajouter une réservation',
				'item_rank' : 1,
				'item_url_name' : 'ajout_reserv'
			},
			'consult_reserv' : {
				'item_img' : settings.STATIC_URL + 'images/thumbnails/gest_reserv/consult_reserv.png',
				'item_name' : 'Consulter une réservation',
				'item_rank' : 2,
				'item_url_name' : 'chois_reserv'
			}
		},
		'mod_name' : 'Gestion des réservations',
		'mod_rank' : 4,
		'mod_rights' : ['A', 'PR'],
		'mod_url_name' : 'gest_reserv'
	},
	'raccs' : {
		'mod_img' : settings.STATIC_URL + 'images/thumbnails/raccs/main.png',
		'mod_items' : {
			'gest_ecoles' : {
				'item_img' : None,
				'item_name' : 'Gestion des écoles',
				'item_rank' : 1,
				'item_url_name' : '__ABS__/admin/app/tecole/'
			}
		},
		'mod_name' : 'Raccourcis',
		'mod_rank' : 6,
		'mod_rights' : '__ALL__',
		'mod_url_name' : 'raccs'
	},
	'real_etats' : {
		'mod_img' : settings.STATIC_URL + 'images/thumbnails/real_etats/main.png',
		'mod_items' : {},
		'mod_name' : 'Réalisation d\'états',
		'mod_rank' : 5,
		'mod_rights' : [],
		'mod_url_name' : None
	}
}

MONTHS = [
	'Janvier',
	'Février',
	'Mars',
	'Avril',
	'Mai',
	'Juin',
	'Juillet',
	'Août',
	'Septembre',
	'Octobre',
	'Novembre',
	'Décembre'
]

PDF_INCLUDE_FILES = ['css/pdf_template.css']

PKS = {
	'id_org__smmar' : config('SMMAR__PK', cast = int),
	'id_type_public__jps' : config('JEUNE_PUBLIC_SCOLAIRE__PK', cast = int),
	'id_type_public__jpes' : config('JEUNE_PUBLIC_EXTRA_SCOLAIRE__PK', cast = int)
}

REQUIRED_FIELD = '<span class="required-field"></span>'

RESERVATION_BOUNDS = { 'AM' : ('AM', 'Matin'), 'PM' : ('PM', 'Après-midi'), 'WD' : ('WD', 'Journée entière') }

SMMAR_SUPPORT = config('SMMAR_SUPPORT', cast = bool)

YEAR_OF_CREATION = 2003