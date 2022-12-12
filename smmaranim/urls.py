# coding: utf-8

# Imports
from app.apps import AppConfig
from app.views import gest_anim
from app.views import gest_marches
from app.views import gest_projets
from app.views import gest_reserv
from app.views import handlers
from app.views import index
from app.views import raccs
from django.conf import settings
from django.conf.urls import handler403
from django.conf.urls import handler404
from django.conf.urls import handler500
from django.urls import re_path
from django.conf.urls.static import static
from django.contrib import admin
from app.views.real_etats import real_etats
from app.views.real_etats.Bilan_Animations_Facturation import Bilan_Animations_Facturation
from app.views.real_etats.Bilan_Projets_Cible_JPS import Bilan_Projets_Cible_JPS

urlpatterns = [
	re_path(r'^admin/', admin.site.urls),
    re_path(r'^index.html$', index.index, name = 'index'),
    re_path(r'^$', index.index, name = 'index'),
    re_path(r'^consulter-compte.html$', index.consult_compte, name = 'consult_compte'),
    re_path(r'^alertes/$', index.get_alert, name = 'get_alert')
]

# Détermination de l'URL pour chacun des modules
module__url = 'modules/'
gest_marches__url = module__url + 'gestion-marches/'
gest_projets__url = module__url + 'gestion-projets/'
gest_anim__url = module__url + 'gestion-animations/'
gest_reserv__url = module__url + 'gestion-reservations/'
raccs__url = module__url + 'raccourcis/'
real_etats__url = module__url + 'real_etats/'

urlpatterns += [
	re_path(r'^{}$'.format(gest_marches__url), gest_marches.get_menu, name = 'gest_marches'),
	re_path(
		r'^{}ajouter-marche/$'.format(gest_marches__url),
		gest_marches.ger_marche,
		{ '_inst' : False },
		name = 'ajout_marche'
	),
	re_path(
		r'^{}modifier-marche/$'.format(gest_marches__url),
		gest_marches.ger_marche,
		{ '_inst' : True },
		name = 'modif_marche'
	),
	re_path(r'^{}choisir-marche/$'.format(gest_marches__url), gest_marches.chois_marche, name = 'chois_marche'),
	re_path(
		r'^{}consulter-marche/([0-9]+)/$'.format(gest_marches__url),
		gest_marches.consult_marche,
		name = 'consult_marche'
	)
]

urlpatterns += [
	re_path(r'^{}$'.format(gest_projets__url), gest_projets.get_menu, name = 'gest_projets'),
	re_path(
		r'^{}ajouter-projet/$'.format(gest_projets__url),
		gest_projets.ger_projet,
		{ '_inst' : False },
		name = 'ajout_projet'
	),
	re_path(
		r'^{}modifier-projet/$'.format(gest_projets__url),
		gest_projets.ger_projet,
		{ '_inst' : True },
		name = 'modif_projet'
	),
	re_path(r'^{}choisir-projet/$'.format(gest_projets__url), gest_projets.chois_projet, name = 'chois_projet'),
	re_path(
		r'^{}consulter-projet/([0-9]+)/$'.format(gest_projets__url),
		gest_projets.consult_projet,
		name = 'consult_projet'
	)
]

urlpatterns += [
	re_path(r'^{}$'.format(gest_anim__url), gest_anim.get_menu, name = 'gest_anim'),
	re_path(
		r'^{}ajouter-animation/$'.format(gest_anim__url),
		gest_anim.ger_anim,
		{ '_inst' : False },
		name = 'ajout_anim'
	),
	re_path(
		r'^{}modifier-animation/$'.format(gest_anim__url),
		gest_anim.ger_anim,
		{ '_inst' : True },
		name = 'modif_anim'
	),
	re_path(r'^{}choisir-animation/$'.format(gest_anim__url), gest_anim.chois_anim, name = 'chois_anim'),
	re_path(
		r'^{}consulter-animation/([0-9]+)/$'.format(gest_anim__url),
		gest_anim.consult_anim,
		name = 'consult_anim'
	)
]

urlpatterns += [
	re_path(r'^{}$'.format(gest_reserv__url), gest_reserv.get_menu, name = 'gest_reserv'),
	re_path(
		r'^{}ajouter-reservation/$'.format(gest_reserv__url),
		gest_reserv.ger_reserv,
		{ '_inst' : False },
		name = 'ajout_reserv'
	),
	re_path(
		r'^{}modifier-reservation/$'.format(gest_reserv__url),
		gest_reserv.ger_reserv,
		{ '_inst' : True },
		name = 'modif_reserv'
	),
	re_path(r'^{}choisir-reservation/$'.format(gest_reserv__url), gest_reserv.chois_reserv, name = 'chois_reserv'),
	re_path(
		r'^{}consulter-reservation/([0-9]+)/$'.format(gest_reserv__url),
		gest_reserv.consult_reserv,
		name = 'consult_reserv'
	)
]

urlpatterns += [
	re_path(r'^{}$'.format(raccs__url), raccs.get_menu, name = 'raccs'),
]

urlpatterns += [
	re_path(r'^{}$'.format(real_etats__url), real_etats.get_menu, name = 'real_etats'),
	re_path(r'^{}bilan-projets-jps/$'.format(real_etats__url), Bilan_Projets_Cible_JPS.as_view(), name = 'bilan_projets_jps'),
	re_path(r'^{}bilan-animations-facturation/$'.format(real_etats__url), Bilan_Animations_Facturation.as_view(), name = 'bilan_animations_facturation'),
]

# Possibilité de consulter les pièces jointes
if settings.DEBUG is True : urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

# Détermination des templates personnalisés pour certains codes d'erreur
handler403 = handlers.handler_403
handler404 = handlers.handler_404
handler500 = handlers.handler_500

# Détermination de certains paramètres du site d'administration
admin.site.index_title = 'Accueil'
admin.site.site_header = 'Administration de {}'.format(AppConfig.verbose_name)
admin.site.site_title = 'Site d\'administration de {}'.format(AppConfig.verbose_name)