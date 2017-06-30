# coding: utf-8

# Imports
from app.apps import AppConfig
from app.views import gest_anim
from app.views import gest_marches
from app.views import gest_projets
from app.views import gest_reserv
from app.views import handlers
from app.views import index
from django.conf import settings
from django.conf.urls import handler403
from django.conf.urls import handler404
from django.conf.urls import handler500
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
	url(r'^admin/', admin.site.urls),
    url(r'^index.html$', index.index, name = 'index'),
    url(r'^$', index.index, name = 'index'),
    url(r'^consulter-compte.html$', index.consult_compte, name = 'consult_compte'),
    url(r'^alertes/$', index.get_alert, name = 'get_alert')
]

# Détermination de l'URL pour chacun des modules
module__url = 'modules/'
gest_marches__url = module__url + 'gestion-marches/'
gest_projets__url = module__url + 'gestion-projets/'
gest_anim__url = module__url + 'gestion-animations/'
gest_reserv__url = module__url + 'gestion-reservations/'

urlpatterns += [
	url(r'^{}$'.format(gest_marches__url), gest_marches.get_menu, name = 'gest_marches'),
	url(
		r'^{}ajouter-marche/$'.format(gest_marches__url),
		gest_marches.ger_marche,
		{ '_inst' : False },
		name = 'ajout_marche'
	),
	url(
		r'^{}modifier-marche/$'.format(gest_marches__url),
		gest_marches.ger_marche,
		{ '_inst' : True },
		name = 'modif_marche'
	),
	url(r'^{}choisir-marche/$'.format(gest_marches__url), gest_marches.chois_marche, name = 'chois_marche'),
	url(
		r'^{}consulter-marche/([0-9]+)/$'.format(gest_marches__url),
		gest_marches.consult_marche,
		name = 'consult_marche'
	)
]

urlpatterns += [
	url(r'^{}$'.format(gest_projets__url), gest_projets.get_menu, name = 'gest_projets'),
	url(
		r'^{}ajouter-projet/$'.format(gest_projets__url),
		gest_projets.ger_projet,
		{ '_inst' : False },
		name = 'ajout_projet'
	),
	url(
		r'^{}modifier-projet/$'.format(gest_projets__url),
		gest_projets.ger_projet,
		{ '_inst' : True },
		name = 'modif_projet'
	),
	url(r'^{}choisir-projet/$'.format(gest_projets__url), gest_projets.chois_projet, name = 'chois_projet'),
	url(
		r'^{}consulter-projet/([0-9]+)/$'.format(gest_projets__url),
		gest_projets.consult_projet,
		name = 'consult_projet'
	)
]

urlpatterns += [
	url(r'^{}$'.format(gest_anim__url), gest_anim.get_menu, name = 'gest_anim'),
	url(
		r'^{}ajouter-animation/$'.format(gest_anim__url),
		gest_anim.ger_anim,
		{ '_inst' : False },
		name = 'ajout_anim'
	),
	url(
		r'^{}modifier-animation/$'.format(gest_anim__url),
		gest_anim.ger_anim,
		{ '_inst' : True },
		name = 'modif_anim'
	),
	url(r'^{}choisir-animation/$'.format(gest_anim__url), gest_anim.chois_anim, name = 'chois_anim'),
	url(
		r'^{}consulter-animation/([0-9]+)/$'.format(gest_anim__url),
		gest_anim.consult_anim,
		name = 'consult_anim'
	)
]

urlpatterns += [
	url(r'^{}$'.format(gest_reserv__url), gest_reserv.get_menu, name = 'gest_reserv'),
	url(
		r'^{}ajouter-reservation/$'.format(gest_reserv__url),
		gest_reserv.ger_reserv,
		{ '_inst' : False },
		name = 'ajout_reserv'
	),
	url(
		r'^{}modifier-reservation/$'.format(gest_reserv__url),
		gest_reserv.ger_reserv,
		{ '_inst' : True },
		name = 'modif_reserv'
	),
	url(r'^{}choisir-reservation/$'.format(gest_reserv__url), gest_reserv.chois_reserv, name = 'chois_reserv'),
	url(
		r'^{}consulter-reservation/([0-9]+)/$'.format(gest_reserv__url),
		gest_reserv.consult_reserv,
		name = 'consult_reserv'
	)
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