# coding: utf-8

'''
Génération d'une chaîne de caractères selon le datetime courant
Retourne une chaîne de caractères
'''
def sub() : import hashlib; import time; return hashlib.sha1(time.strftime('%d%m%Y%H%M%S').encode()).hexdigest()