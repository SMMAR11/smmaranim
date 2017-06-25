# coding: utf-8

# Import
from app.functions.handler_init import sub

def handler_403(_req) : return sub(_req, 403, 'L\'accès à cette page est interdit.')
def handler_404(_req) : return sub(_req, 404, 'La page que vous recherchez n\'existe pas ou a été déplacée.')
def handler_500(_req) : return sub(_req, 500, 'Erreur interne du serveur.')