# coding: utf-8

# Imports
from django.contrib.auth.models import User
from django.db import models

class TTypeUtilisateur(models.Model) :

	# Attributs
	code_type_util = models.CharField(max_length = 5, primary_key = True)
	int_type_util = models.CharField(max_length = 255)

	class Meta :
		db_table = 't_type_utilisateur'
		ordering = ['int_type_util']
		verbose_name = verbose_name_plural = 'T_TYPE_UTILISATEUR'

	# Getters
	def get_pk(self) : return self.pk
	def get_int_type_util(self) : return self.int_type_util

	def __str__(self) : return self.get_int_type_util()

class TOrganisme(models.Model) :

	# Attributs
	id_org = models.AutoField(primary_key = True)
	coul_org = models.CharField(
		default = 'revert',
		help_text = '''
		Au format suivant : caractère dièse (#) suivi de six caractères (chiffres ou lettres de A à F inclus). Valeur
		« revert » acceptée.
		''',
		max_length = 255,
		verbose_name = 'Couleur HTML hexadécimale'
	)
	est_prest = models.BooleanField(default = True, verbose_name = 'L\'organisme est-il prestataire ?')
	nom_org = models.CharField(max_length = 255, verbose_name = 'Nom de l\'organisme')

	class Meta :
		db_table = 't_organisme'
		ordering = ['nom_org']
		verbose_name = verbose_name_plural = 'T_ORGANISME'

	# Getters
	def get_pk(self) : return self.pk
	def get_coul_org(self) : return self.coul_org
	def get_est_prest(self) : return self.est_prest
	def get_nom_org(self) : return self.nom_org

	# Autres getters
	def get_pm(self) : return self.tprestatairesmarche_set

	def __str__(self) : return self.get_nom_org()

	def clean(self) :

		# Imports
		from django.core.exceptions import ValidationError
		from smmaranim.custom_settings import ERROR_MESSAGES
		import re

		# Renvoi d'une erreur en cas de renseignement d'une couleur inexistante
		if self.get_coul_org() != 'revert' :
			if not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', self.get_coul_org()) :
				raise ValidationError({ 'coul_org' : ERROR_MESSAGES['invalid'] })

class TUtilisateur(User) :

	# Attribut
	en_mode_superadmin = models.BooleanField(default = False)
	id_org = models.ForeignKey(TOrganisme, on_delete = models.CASCADE, verbose_name = 'Organisme')

	# Relation
	type_util = models.ManyToManyField(TTypeUtilisateur, through = 'TDroitsUtilisateur')

	class Meta :
		db_table = 't_utilisateur'
		ordering = ['username']
		verbose_name = verbose_name_plural = 'T_UTILISATEUR'

	# Getters
	def get_pk(self) : return self.pk
	def get_date_joined(self) : return self.date_joined
	def get_email(self) : return self.email
	def get_en_mode_superadmin(self) : return self.en_mode_superadmin
	def get_first_name(self) : return self.first_name
	def get_is_active(self) : return self.is_active
	def get_is_staff(self) : return self.is_staff
	def get_is_superuser(self) : return self.is_superuser
	def get_last_login(self) : return self.last_login
	def get_last_name(self) : return self.last_name
	def get_org(self) : return self.id_org
	def get_type_util(self) : return self.type_util
	def get_username(self) : return self.username

	# Autres getters
	def get_du(self) : return self.tdroitsutilisateur_set

	# Méthodes
	def can_access(self, _o, _f = True) :

		# Import
		from django.core.exceptions import PermissionDenied

		acces = True if self.get_org() == _o else False
		if _f == True :
			return acces
		else :
			if acces == False : raise PermissionDenied

	def get_cal_anim(self, _mois, _annee) :
		from app.functions.calendar_init import sub; return sub(self, _mois, _annee)
	def get_est_superadmin(self) :
		if 'A' in self.get_type_util__list() :
			if self.get_en_mode_superadmin() == True :
				output = 1
			else :
				output = 0
		else :
			output = -1
		return output

	def get_menu(self) :

		# Imports
		from collections import OrderedDict
		from smmaranim.custom_settings import MENU

		output = {}

		# Définition des modules accessibles par l'utilisateur
		for cle, val in MENU.items() :
			if val['mod_rights'] == '__ALL__' or set(self.get_type_util__list()).intersection(val['mod_rights']) :
				output[cle] = val

		# Tri des éléments de chaque module par ordre d'affichage
		for elem in output.values() :
			elem['mod_items'] = OrderedDict(sorted(elem['mod_items'].items(), key = lambda l : l[1]['item_rank']))

		# Tri des modules par ordre d'affichage
		output = OrderedDict(sorted(output.items(), key = lambda l : l[1]['mod_rank']))

		return output

	def get_nom_complet(self) : return '{} {}'.format(self.get_last_name(), self.get_first_name())
	def get_type_util__list(self) : return [tu.get_pk() for tu in self.get_type_util().all()]
	def get_util_connect(_req) :
		from app.models import TUtilisateur
		return TUtilisateur.objects.get(pk = _req.user.pk) if _req.user.is_authenticated() else None

	def __str__(self) : return self.get_username()

class TDroitsUtilisateur(models.Model) :

	# Attributs
	code_type_util = models.ForeignKey(TTypeUtilisateur, on_delete = models.CASCADE)
	id_util = models.ForeignKey(TUtilisateur, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_droits_utilisateur'
		verbose_name = verbose_name_plural = 'T_DROITS_UTILISATEUR'

	# Getters
	def get_pk(self) : return self.pk
	def get_type_util(self) : return self.code_type_util
	def get_util(self) : return self.id_util

	def __str__(self) : return '{} - {}'.format(self.get_util(), self.get_type_util())

class TMarche(models.Model) :

	# Import
	from django.contrib.postgres.fields import ArrayField

	# Attributs
	id_marche = models.AutoField(primary_key = True)
	dt_marche = ArrayField(base_field = models.DateField(), size = 2)
	int_marche = models.CharField(max_length = 255, verbose_name = 'Intitulé du marché')

	# Relation
	prest = models.ManyToManyField(TOrganisme, through = 'TPrestatairesMarche')

	class Meta :
		db_table = 't_marche'
		ordering = ['-dt_marche', 'int_marche']
		verbose_name = verbose_name_plural = 'T_MARCHE'

	# Getters
	def get_pk(self) : return self.pk
	def get_dt_marche(self) : return self.dt_marche
	def get_int_marche(self) : return self.int_marche
	def get_prest(self) : return self.prest

	# Autres getters
	def get_pm(self) : return self.tprestatairesmarche_set

	# Méthodes
	def get_dt_marche__str(self) :
		from app.functions.get_local_format import sub; return [sub(elem) for elem in self.get_dt_marche()]
	def get_prest__str(self) : return ', '.join([str(p) for p in self.get_prest().all()]) or '-'

	def __str__(self) : return '{} (du {} au {})'.format(self.get_int_marche(), *self.get_dt_marche__str())

class TPrestatairesMarche(models.Model) :

	# Imports
	from app.validators import valid_dj
	from django.core.validators import MinValueValidator

	# Attributs
	id_marche = models.ForeignKey(TMarche, on_delete = models.CASCADE)
	id_prest = models.ForeignKey(TOrganisme, on_delete = models.CASCADE)
	nbre_dj_ap_pm = models.FloatField(
		default = 0,
		validators = [MinValueValidator(0), valid_dj],
		verbose_name = 'Nombre de demi-journées pour les animations ponctuelles'
	)
	nbre_dj_pp_pm = models.FloatField(
		default = 0,
		validators = [MinValueValidator(0), valid_dj],
		verbose_name = 'Nombre de demi-journées pour les programmes pédagogiques'
	)

	class Meta :
		db_table = 't_prestataires_marche'
		verbose_name = verbose_name_plural = 'T_PRESTATAIRES_MARCHE'

	# Getters
	def get_pk(self) : return self.pk
	def get_marche(self) : return self.id_marche
	def get_prest(self) : return self.id_prest
	def get_nbre_dj_ap_pm(self) : return self.nbre_dj_ap_pm
	def get_nbre_dj_pp_pm(self) : return self.nbre_dj_pp_pm

	# Autres getters
	def get_projet(self) : return self.tprojet_set
	def get_tdj(self) : return self.ttransactiondemijournees_set

	# Méthodes
	def get_nbre_dj_ap_pm__str(self) : return '{0:g}'.format(self.get_nbre_dj_ap_pm())
	def get_nbre_dj_pp_pm__str(self) : return '{0:g}'.format(self.get_nbre_dj_pp_pm())
	def get_nbre_dj_progr_pm(self, _ti, _str = True) :
		vals = []
		for p in self.get_projet().all() :
			if p.get_type_interv().get_pk() == _ti :
				for a in p.get_anim().all() : vals.append(a.get_nbre_dj_anim())
		output = sum(vals)
		return '{0:g}'.format(output) if _str == True else output
	def get_nbre_dj_prep_real_pm(self, _progr, _str = True) :
		if _progr == True :
			output = sum([tdj.get_nbre_dj_tdj_progr() for tdj in self.get_tdj().all()])
		else :
			output = sum([tdj.get_nbre_dj_tdj_util() for tdj in self.get_tdj().all()])
		return '{0:g}'.format(output) if _str == True else output
	def get_nbre_dj_ap_rest_pm(self, _str = True) :
		output = self.get_nbre_dj_ap_pm() - self.get_nbre_dj_progr_pm('AP', False)
		return '{0:g}'.format(output) if _str == True else output
	def get_nbre_dj_pp_rest_pm(self, _per, _str = True) :
		terme_1 = self.get_nbre_dj_pp_pm() if _per == False else \
		self.get_nbre_dj_pp_pm() + self.get_nbre_dj_prep_real_pm(True, False)
		terme_2 = self.get_nbre_dj_progr_pm('PP', False) if _per == False else \
		self.get_nbre_dj_progr_pm('PP', False) + self.get_nbre_dj_prep_real_pm(False, False)
		output = terme_1 - terme_2
		return '{0:g}'.format(output) if _str == True else output

	def __str__(self) : return '{} - {}'.format(self.get_prest(), self.get_marche())

class TTransactionDemiJournees(models.Model) :

	# Imports
	from app.validators import valid_dj
	from django.core.validators import MinValueValidator

	# Attributs
	id_tdj = models.AutoField(primary_key = True)
	int_tdj = models.CharField(max_length = 255, verbose_name = 'Intitulé')
	nbre_dj_tdj_progr = models.FloatField(
		default = 0, validators = [MinValueValidator(0), valid_dj], verbose_name = 'Nombre de demi-journées prévues'
	)
	nbre_dj_tdj_util = models.FloatField(
		default = 0, validators = [MinValueValidator(0), valid_dj], verbose_name = 'Nombre de demi-journées utilisées'
	)
	id_pm = models.ForeignKey(TPrestatairesMarche, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_transaction_demi_journees'
		ordering = ['int_tdj']
		verbose_name = verbose_name_plural = 'T_TRANSACTION_DEMI_JOURNEES'

	# Getters
	def get_pk(self) : return self.pk
	def get_int_tdj(self) : return self.int_tdj
	def get_nbre_dj_tdj_progr(self) : return self.nbre_dj_tdj_progr
	def get_nbre_dj_tdj_util(self) : return self.nbre_dj_tdj_util
	def get_pm(self) : return self.id_pm

	# Méthodes
	def get_nbre_dj_tdj_progr__str(self) : return '{0:g}'.format(self.get_nbre_dj_tdj_progr())
	def get_nbre_dj_tdj_util__str(self) : return '{0:g}'.format(self.get_nbre_dj_tdj_util())

	def __str__(self) :
		return '{} - {}'.format(self.get_pm(), self.get_int_tdj())

class TTypeIntervention(models.Model) :

	# Attributs
	code_type_interv = models.CharField(max_length = 2, primary_key = True)
	int_type_interv = models.CharField(max_length = 255)

	class Meta :
		db_table = 't_type_intervention'
		ordering = ['int_type_interv']
		verbose_name = verbose_name_plural = 'T_TYPE_INTERVENTION'

	# Getters
	def get_pk(self) : return self.pk
	def get_int_type_interv(self) : return self.int_type_interv

	# Autres getters
	def get_sti(self) : return self.tsoustypeintervention_set

	def __str__(self) : return self.get_int_type_interv()

class TSousTypeIntervention(models.Model) :

	# Attributs
	id_sti = models.AutoField(primary_key = True)
	int_sti = models.CharField(max_length = 255, verbose_name = 'Intitulé de l\'événement')
	id_type_interv = models.ForeignKey(
		TTypeIntervention, on_delete = models.CASCADE, verbose_name = 'Type d\'intervention'
	)

	class Meta :
		db_table = 't_sous_type_intervention'
		ordering = ['int_sti']
		verbose_name = verbose_name_plural = 'T_SOUS_TYPE_INTERVENTION'

	# Getters
	def get_pk(self) : return self.pk
	def get_int_sti(self) : return self.int_sti
	def get_type_interv(self) : return self.id_type_interv

	def __str__(self) : return self.get_int_sti()

class TCommune(models.Model) :

	# Attributs
	code_comm = models.CharField(max_length = 5, primary_key = True, verbose_name = 'Code INSEE de la commune')
	nom_comm = models.CharField(max_length = 255, verbose_name = 'Nom de la commune')

	class Meta :
		db_table = 't_commune'
		ordering = ['code_comm']
		verbose_name = verbose_name_plural = 'T_COMMUNE'

	# Getters
	def get_pk(self) : return self.pk
	def get_nom_comm(self) : return self.nom_comm

	def __str__(self) : return '{} ({})'.format(self.get_nom_comm(), self.get_pk())

class TStructure(models.Model) :

	# Attributs
	id_struct = models.AutoField(primary_key = True)
	int_struct = models.CharField(max_length = 255, verbose_name = 'Intitulé de la structure')
	ordre_ld_struct = models.PositiveIntegerField(default = 9999, verbose_name = 'Ordre dans la liste déroulante')

	class Meta :
		db_table = 't_structure'
		ordering = ['ordre_ld_struct', 'int_struct']
		verbose_name = verbose_name_plural = 'T_STRUCTURE'

	# Getters
	def get_pk(self) : return self.pk
	def get_int_struct(self) : return self.int_struct
	def get_ordre_ld_struct(self) : return self.ordre_ld_struct

	def __str__(self) : return self.get_int_struct()

class TTypePublic(models.Model) :

	# Attributs
	id_type_public = models.AutoField(primary_key = True)
	int_type_public = models.CharField(max_length = 255, verbose_name = 'Intitulé du type de public')

	class Meta :
		db_table = 't_type_public'
		ordering = ['int_type_public']
		verbose_name = verbose_name_plural = 'T_TYPE_PUBLIC'

	# Getters
	def get_pk(self) : return self.pk
	def get_int_type_public(self) : return self.int_type_public

	def __str__(self) : return self.get_int_type_public()


class TEcole(models.Model) :

	# Attributs
	id_ecole = models.AutoField(primary_key = True)
	nom_ecole = models.CharField(max_length = 255, verbose_name = 'Nom de l\'établissement')
	code_comm = models.ForeignKey(TCommune, on_delete = models.CASCADE, verbose_name = 'Commune')

	class Meta :
		db_table = 't_ecole'
		ordering = ['nom_ecole']
		verbose_name = verbose_name_plural = 'T_ECOLE'

	# Getters
	def get_pk(self) : return self.pk
	def get_comm(self) : return self.code_comm
	def get_nom_ecole(self) : return self.nom_ecole

	def __str__(self) : return '{} - {}'.format(self.get_nom_ecole(), self.get_comm())

class TClasse(models.Model) :

	# Attributs
	id_classe = models.AutoField(primary_key = True)
	int_classe = models.CharField(max_length = 255, verbose_name = 'Intitulé de la classe')
	ordre_ld_classe = models.PositiveIntegerField(default = 9999, verbose_name = 'Ordre dans la liste déroulante')

	class Meta :
		db_table = 't_classe'
		ordering = ['ordre_ld_classe', 'int_classe']
		verbose_name = verbose_name_plural = 'T_CLASSE'

	# Getters
	def get_pk(self) : return self.pk
	def get_int_classe(self) : return self.int_classe
	def get_ordre_ld_classe(self) : return self.ordre_ld_classe

	def __str__(self) : return self.get_int_classe()

class TProjet(models.Model) :

	# Import
	from django.core.validators import RegexValidator

	# Attributs
	id_projet = models.AutoField(primary_key = True)
	comm_projet = models.TextField(blank = True, null = True, verbose_name = 'Commentaire')
	courr_refer_projet = models.EmailField(blank = True, null = True, verbose_name = 'Courriel du contact référent')
	int_projet = models.CharField(max_length = 255, verbose_name = 'Intitulé du projet')
	nom_refer_projet = models.CharField(max_length = 255, verbose_name = 'Nom de famille du contact référent')
	prenom_refer_projet = models.CharField(
		blank = True, max_length = 255, null = True, verbose_name = 'Prénom du contact référent'
	)
	tel_refer_projet = models.CharField(
		blank = True,
		max_length = 10,
		null = True,
		validators = [RegexValidator(r'^[0-9]{10}')],
		verbose_name = 'Numéro de téléphone du contact référent'
	)
	id_org = models.ForeignKey(TOrganisme, on_delete = models.CASCADE)
	id_pm = models.ForeignKey(TPrestatairesMarche, null = True, on_delete = models.CASCADE)
	id_sti = models.ForeignKey(TSousTypeIntervention, null = True, on_delete = models.CASCADE)
	id_type_public = models.ForeignKey(TTypePublic, on_delete = models.CASCADE, verbose_name = 'Type de public visé')

	class Meta :
		db_table = 't_projet'
		ordering = ['int_projet']
		verbose_name = verbose_name_plural = 'T_PROJET'

	def clean(self) :

		# Imports
		from django.core.exceptions import ValidationError
		from smmaranim.custom_settings import ERROR_MESSAGES

		# Renvoi d'une erreur si aucune adresse électronique et aucun numéro de téléphone
		if self.get_nom_refer_projet() :
			if not self.get_courr_refer_projet() and not self.get_tel_refer_projet() :
				raise ValidationError({ '__all__' : ERROR_MESSAGES['email_or_phone_number'] })

	# Getters
	def get_pk(self) : return self.pk
	def get_comm_projet(self) : return self.comm_projet
	def get_courr_refer_projet(self) : return self.courr_refer_projet
	def get_int_projet(self) : return self.int_projet
	def get_nom_refer_projet(self) : return self.nom_refer_projet
	def get_prenom_refer_projet(self) : return self.prenom_refer_projet
	def get_tel_refer_projet(self) : return self.tel_refer_projet
	def get_org(self) : return self.id_org
	def get_pm(self) : return self.id_pm
	def get_sti(self) : return self.id_sti
	def get_type_public(self) : return self.id_type_public

	# Autres getters
	def get_anim(self) : return self.tanimation_set
	def get_cep(self) : return self.tclassesecoleprojet_set
	def get_ta(self) : return self.ttrancheage_set

	# Méthodes
	def get_attrs_projet(self, _pdf = False) :

		# Imports
		from app.functions.attributes_init import sub
		from django.core.urlresolvers import reverse

		# Initialisation des attributs du projet
		attrs = {
			'anims' : {
				'label' : 'Animation(s)',
				'value' : [[
					a.get_projet().get_org(),
					a.get_dt_heure_anim__str(),
					a.get_nat_anim(),
					a.get_lieu_anim(),
					a.get_comm(),
					'''
					<a href="{}" class="inform-icon pull-right" title="Consulter l\'animation"></a>
					'''.format(reverse('consult_anim', args = [a.get_pk()]))
				] for a in self.get_anim().all()],
				'table' : True,
				'table_header' : [[
					['Organisme', None],
					['Date et heure de l\'animation', None],
					['Nature de l\'animation', None],
					['Lieu de l\'animation', None],
					['Commune accueillant l\'animation', None],
					['', None]
				]]
			},
			'comm_projet' : { 'label' : 'Commentaire', 'value' : self.get_comm_projet() },
			'courr_refer_projet' : { 
				'label' : 'Courriel du contact référent', 'value' : self.get_courr_refer_projet()
			},
			'int_projet' : { 'label' : 'Intitulé du projet', 'value' : self.get_int_projet() },
			'marche' : { 'label' : 'Marché', 'value' : self.get_pm().get_marche() if self.get_pm() else None },
			'org' : { 'label' : 'Organisme', 'value' : self.get_org() },
			'refer_projet' : { 'label' : 'Nom complet du contact référent', 'value' : self.get_nom_complet() },
			'sti' : { 'label' : 'Événement', 'value' : self.get_sti() },
			'tel_refer_projet' : {
				'label' : 'Numéro de téléphone du contact référent',
				'value' : self.get_tel_refer_projet__deconstructed()
			},
			'type_interv' : { 'label' : 'Type d\'intervention', 'value' : self.get_type_interv() },
			'type_public' : { 'label' : 'Type de public visé', 'value' : self.get_type_public() }
		}

		return sub(attrs, _pdf)

	def get_nom_complet(self) : return '{} {}'.format(self.get_nom_refer_projet(), self.get_prenom_refer_projet())
	def get_tel_refer_projet__deconstructed(self) :
		t = iter(self.get_tel_refer_projet()); return '-'.join(a + b for a, b in zip(t, t))
	def get_type_interv(self) :
		from app.models import TTypeIntervention
		return self.get_sti().get_type_interv() if self.get_sti() else TTypeIntervention.objects.get(pk = 'AP')

	def __str__(self) :  return self.get_int_projet()

class TClassesEcoleProjet(models.Model) :

	# Import
	from django.core.validators import RegexValidator

	# Attributs
	id_classe = models.ForeignKey(TClasse, on_delete = models.CASCADE, verbose_name = 'Classe')
	id_ecole = models.ForeignKey(TEcole, on_delete = models.CASCADE, verbose_name = 'Établissement scolaire')
	id_projet = models.ForeignKey(TProjet, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_classes_ecole_projet'
		ordering = ['id_classe', 'id_ecole']
		verbose_name = verbose_name_plural = 'T_CLASSES_ECOLE_PROJET'

	# Getters
	def get_pk(self) : return self.pk
	def get_classe(self) : return self.id_classe
	def get_ecole(self) : return self.id_ecole
	def get_projet(self) : return self.id_projet

	def __str__(self) : return '{} - {} - {}'.format(self.get_projet(), self.get_classe(), self.get_ecole())

class TTrancheAge(models.Model) :

	# Attributs
	id_ta = models.AutoField(primary_key = True)
	int_struct_ta = models.CharField(max_length = 255, verbose_name = 'Structure d\'accueil')
	min_ta = models.PositiveIntegerField(verbose_name = 'Âge minimum')
	max_ta = models.PositiveIntegerField(verbose_name = 'Âge maximum')
	id_projet = models.ForeignKey(TProjet, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_tranche_age'
		ordering = ['min_ta', 'max_ta', 'int_struct_ta']
		verbose_name = verbose_name_plural = 'T_TRANCHE_AGE'

	# Getters
	def get_pk(self) : return self.pk
	def get_int_struct_ta(self) : return self.int_struct_ta
	def get_min_ta(self) : return self.min_ta
	def get_max_ta(self) : return self.max_ta
	def get_projet(self) : return self.id_projet

	def __str__(self) :
		return '{} - {} - ({}-{} ans)'.format(
			self.get_projet(),
			self.get_int_struct_ta(),
			self.get_min_ta(),
			self.get_max_ta()
		)

class TAnimation(models.Model) :

	# Imports
	from django.contrib.postgres.fields import ArrayField
	from smmaranim.custom_settings import HALF_DAY_CHOICES

	# Attributs
	id_anim = models.AutoField(primary_key = True)
	dt_anim = models.DateField(verbose_name = 'Date de l\'animation')
	est_anim = models.BooleanField(default = True, verbose_name = 'L\'animation est-elle un rendez-vous ?')
	heure_anim = ArrayField(base_field = models.TimeField(), size = 2)
	lieu_anim = models.CharField(max_length = 255, verbose_name = 'Lieu de l\'animation')
	nbre_dj_anim = models.FloatField(
		blank = True,
		choices = [(elem, str(elem)) for elem in HALF_DAY_CHOICES],
		null = True,
		verbose_name = 'Nombre de demi-journées déduites'
	)
	num_anim = models.PositiveIntegerField(
		blank = True, null = True, verbose_name = 'Numéro de l\'animation ou du rendez-vous'
	)
	code_comm = models.ForeignKey(TCommune, on_delete = models.CASCADE)
	id_projet = models.ForeignKey(TProjet, on_delete = models.CASCADE, verbose_name = 'Projet')
	id_struct = models.ForeignKey(TStructure, on_delete = models.CASCADE, verbose_name = 'Structure d\'accueil')

	class Meta :
		db_table = 't_animation'
		ordering = ['dt_anim', 'heure_anim']
		verbose_name = verbose_name_plural = 'T_ANIMATION'

	# Getters
	def get_pk(self) : return self.pk
	def get_comm(self) : return self.code_comm
	def get_dt_anim(self) : return self.dt_anim
	def get_est_anim(self) : return self.est_anim
	def get_heure_anim(self) : return self.heure_anim
	def get_lieu_anim(self) : return self.lieu_anim
	def get_nbre_dj_anim(self) : return self.nbre_dj_anim or 0
	def get_num_anim(self) : return self.num_anim
	def get_projet(self) : return self.id_projet
	def get_struct(self) : return self.id_struct

	# Autres getters
	def get_bilan(self) : return self.tbilan_set

	# Méthodes
	def get_attrs_anim(self, _pdf = False) :

		# Import
		from app.functions.attributes_init import sub

		# Initialisation des attributs de l'animation
		attrs = {
			'comm' : { 'label' : 'Commune accueillant l\'animation', 'value' : self.get_comm() },
			'dt_heure_anim' : { 'label' : 'Date et heure de l\'animation', 'value' : self.get_dt_heure_anim__str() },
			'lieu_anim' : { 'label' : 'Lieu de l\'animation', 'value' : self.get_lieu_anim() },
			'nat_anim' : { 'label' : 'Nature de l\'animation', 'value' : self.get_nat_anim() },
			'prest' : { 'label' : 'Organisme', 'value' : self.get_projet().get_org() },
			'struct' : { 'label' : 'Structure d\'accueil', 'value' : self.get_struct() },
			'projet' : { 'label' : 'Projet', 'value' : self.get_projet() }
		}

		if self.get_projet().get_org().get_est_prest() == True :
			attrs['nbre_dj_anim'] = {
				'label' : 'Nombre de demi-journées déduites', 'value' : self.get_nbre_dj_anim__str()
			}

		return sub(attrs, _pdf)

	def get_bilan__object(self) : return self.get_bilan().get() if self.get_bilan().count() > 0 else None
	def get_dt_anim__str(self) :
		from app.functions.get_local_format import sub; return sub(self.get_dt_anim())
	def get_dt_heure_anim__str(self) :
		return '{} {}'.format(self.get_dt_anim__str(), '-'.join(self.get_heure_anim__str()))
	def get_nat_anim(self) :
		return '{} {}'.format('Anim' if self.get_est_anim() == True else 'RDV', self.get_num_anim() or '')
	def get_nbre_dj_anim__str(self) : return '{0:g}'.format(self.get_nbre_dj_anim())
	def get_heure_anim__str(self) :
		from app.functions.get_local_format import sub; return [sub(elem) for elem in self.get_heure_anim() if elem]

	def __str__(self) : 
		return '{} : {} {} ({})'.format(
			'-'.join(self.get_heure_anim__str()),
			self.get_nat_anim(),
			self.get_lieu_anim(),
			self.get_comm().get_nom_comm()
		)

class TBilan(models.Model) :

	# Attributs
	id_bilan = models.AutoField(primary_key = True)
	comm_bilan = models.TextField(blank = True, null = True, verbose_name = 'Commentaire')
	fonct_refer_bilan = models.CharField(
		blank = True, max_length = 255, null = True, verbose_name = 'Fonction du contact référent de l\'animation'
	)
	nom_refer_bilan = models.CharField(
		blank = True, max_length = 255, null = True, verbose_name = 'Nom de famille du contact référent de l\'animation'
	)
	prenom_refer_bilan = models.CharField(
		blank = True, max_length = 255, null = True, verbose_name = 'Prénom du contact référent de l\'animation'
	)
	struct_refer_bilan = models.CharField(
		blank = True, max_length = 255, null = True, verbose_name = 'Structure du contact référent de l\'animation'
	)
	id_anim = models.ForeignKey(TAnimation, on_delete = models.CASCADE)
	id_util = models.ForeignKey(TUtilisateur, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_bilan'
		verbose_name = verbose_name_plural = 'T_BILAN'

	# Getters
	def get_pk(self) : return self.pk
	def get_comm_bilan(self) : return self.comm_bilan
	def get_fonct_refer_bilan(self) : return self.fonct_refer_bilan
	def get_nom_refer_bilan(self) : return self.nom_refer_bilan
	def get_prenom_refer_bilan(self) : return self.prenom_refer_bilan
	def get_struct_refer_bilan(self) : return self.struct_refer_bilan
	def get_anim(self) : return self.id_anim
	def get_util(self) : return self.id_util

	# Autres getters
	def get_ba(self) : return self.tbilananimation if hasattr(self, 'tbilananimation') else None

	# Méthodes
	def get_attrs_bilan(self, _pdf = False, _initial_dict = False) :

		# Import
		from app.functions.attributes_init import sub

		attrs_bilan = {
			'anim' : { 'label' : 'Animation', 'value' : self.get_anim() },
			'comm_bilan' : { 'label' : 'Commentaire', 'value' : self.get_comm_bilan() },
			'fonct_refer_bilan' : { 'label' : 'Fonction du contact référent', 'value' : self.get_fonct_refer_bilan() },
			'org' : { 'label' : 'Organisme', 'value' : self.get_util().get_org() },
			'refer_bilan' : { 'label' : 'Nom complet du contact référent', 'value' : self.get_nom_complet() },
			'struct_refer_bilan' : {
				'label' : 'Structure du contact référent', 'value' : self.get_fonct_refer_bilan()
			},
			'util' : {
				'label' : 'Utilisateur ayant effectué la dernière modification',
				'value' : self.get_util().get_nom_complet()
			}
		}

		return sub(attrs_bilan, _pdf) if _initial_dict == False else attrs_bilan

	def get_nom_complet(self) :
		if self.get_nom_refer_bilan() or self.get_prenom_refer_bilan() :
			return '{} {}'.format(self.get_nom_refer_bilan(), self.get_prenom_refer_bilan())
		else :
			return None

	def __str__(self) : return '{} [BILAN]'.format(self.get_anim())

class TPlaquette(models.Model) :

	# Import
	from app.validators import valid_fich
	from app.validators import valid_pdf

	# Méthodes liées aux attributs
	def set_miniat_plaq__upload_to(_inst, _fn) :
		from app.functions.gen_string import sub
		return 'plaquettes/miniatures/{}.{}'.format(sub(), _fn.split('.')[-1])
	def set_pdf_plaq__upload_to(_inst, _fn) :
		from app.functions.gen_string import sub; return 'plaquettes/pdf/{}.{}'.format(sub(), _fn.split('.')[-1])

	# Attributs
	id_plaq = models.AutoField(primary_key = True)
	int_plaq = models.CharField(max_length = 255, verbose_name = 'Intitulé de la plaquette')
	miniat_plaq = models.ImageField(
		help_text = 'Au format image.',
		upload_to = set_miniat_plaq__upload_to,
		validators = [valid_fich],
		verbose_name = 'Miniature de la plaquette'
	)
	pdf_plaq = models.FileField(
		upload_to = set_pdf_plaq__upload_to,
		validators = [valid_fich, valid_pdf],
		verbose_name = 'Fichier PDF de la plaquette'
	)

	class Meta :
		db_table = 't_plaquette'
		ordering = ['int_plaq']
		verbose_name = verbose_name_plural = 'T_PLAQUETTE'

	# Getters
	def get_pk(self) : return self.pk
	def get_int_plaq(self) : return self.int_plaq
	def get_miniat_plaq(self) : return self.miniat_plaq
	def get_pdf_plaq(self) : return self.pdf_plaq

	# Méthodes
	def get_miniat_plaq__img(self, _kwargs = {}) :

		# Import
		from django.conf import settings

		# Initialisation des arguments
		kwargs = {}
		for cle, val in _kwargs.items() : kwargs[cle] = val
		kwargs['src'] = '{}{}'.format(settings.MEDIA_URL, self.get_miniat_plaq())

		return '<img {}/>'.format(' '.join(['{}="{}"'.format(cle, val) for cle, val in kwargs.items()]))

	def get_plaq__a_img(self, _a_kwargs = {}, _img_kwargs = {}) :

		# Import
		from django.conf import settings

		# Initialisation des arguments de la balise <a/>
		a_kwargs = {}
		for cle, val in _a_kwargs.items() : a_kwargs[cle] = val
		a_kwargs['href'] = '{}{}'.format(settings.MEDIA_URL, self.get_pdf_plaq())

		return '<a {}>{}</a>'.format(
			' '.join(['{}="{}"'.format(cle, val) for cle, val in a_kwargs.items()]),
			self.get_miniat_plaq__img(_img_kwargs)
		)

	def __str__(self) : return self.get_int_plaq()

	def delete(self, *args, **kwargs) :
		self.get_pdf_plaq().delete(); self.get_miniat_plaq().delete(); super(TPlaquette, self).delete(*args, **kwargs)

class TBilanAnimation(TBilan) :

	# Import
	from app.validators import valid_fich
	from app.validators import valid_pdf
	from smmaranim.custom_settings import EVALUATION_CHOICES

	# Méthodes liées aux attributs
	def set_outil_ba__upload_to(_inst, _fn) :
		from app.functions.gen_string import sub; return 'outils_speciaux/{}.{}'.format(sub(), _fn.split('.')[-1])
	def set_photo_ba__upload_to(_inst, _fn) :
		from app.functions.gen_string import sub; return 'animations/photos/{}.{}'.format(sub(), _fn.split('.')[-1])
	def set_rdp_ba__upload_to(_inst, _fn) :
		from app.functions.gen_string import sub
		return 'animations/revues_de_presse/{}.{}'.format(sub(), _fn.split('.')[-1])

	# Attributs
	deroul_ba = models.TextField(blank = True, null = True, verbose_name = 'Déroulement et méthodes adoptées')
	en_exter = models.BooleanField(default = False, verbose_name = 'Y a-t-il eu des activités en extérieur ?')
	en_inter = models.BooleanField(default = False, verbose_name = 'Y a-t-il eu des activités en intérieur ?')
	eval_ba = models.CharField(
		choices = [(elem, elem) for elem in EVALUATION_CHOICES],
		default = 'TOP',
		max_length = 4,
		verbose_name = 'Évaluation de l\'animation'
	)
	nbre_pers_pres_ba = models.PositiveIntegerField(
		blank = True, null = True, verbose_name = 'Nombre de personnes présentes à l\'animation'
	)
	outil_ba = models.FileField(
		blank = True,
		null = True,
		upload_to = set_outil_ba__upload_to,
		validators = [valid_fich],
		verbose_name = 'Outil créé spécialement pour l\'animation'
	)
	photo_1_ba = models.ImageField(
		blank = True,
		null = True,
		upload_to = set_photo_ba__upload_to,
		validators = [valid_fich],
		verbose_name = 'Photo 1 de l\'animation'
	)
	photo_2_ba = models.ImageField(
		blank = True,
		null = True,
		upload_to = set_photo_ba__upload_to,
		validators = [valid_fich],
		verbose_name = 'Photo 2 de l\'animation'
	)
	photo_3_ba = models.ImageField(
		blank = True,
		null = True,
		upload_to = set_photo_ba__upload_to,
		validators = [valid_fich],
		verbose_name = 'Photo 3 de l\'animation'
	)
	rdp_1_ba = models.FileField(
		blank = True,
		null = True,
		upload_to = set_rdp_ba__upload_to,
		validators = [valid_fich, valid_pdf],
		verbose_name = 'Revue de presse 1 de l\'animation <span class="fl-complement">(fichier PDF)</span>'
	)
	rdp_2_ba = models.FileField(
		blank = True,
		null = True,
		upload_to = set_rdp_ba__upload_to,
		validators = [valid_fich, valid_pdf],
		verbose_name = 'Revue de presse 2 de l\'animation <span class="fl-complement">(fichier PDF)</span>'
	)
	rdp_3_ba = models.FileField(
		blank = True,
		null = True,
		upload_to = set_rdp_ba__upload_to,
		validators = [valid_fich, valid_pdf],
		verbose_name = 'Revue de presse 3 de l\'animation <span class="fl-complement">(fichier PDF)</span>'
	)
	themat_abord_ba = models.TextField(verbose_name = 'Thématiques abordées')
	titre_ba = models.CharField(max_length = 255, verbose_name = 'Titre de l\'animation')

	# Relation
	plaq = models.ManyToManyField(TPlaquette, through = 'TPlaquettesDistribuees')

	class Meta :
		db_table = 't_bilan_animation'
		verbose_name = verbose_name_plural = 'T_BILAN_ANIMATION'

	# Getters
	def get_pk(self) : return self.pk
	def get_cep(self) : return self.cep
	def get_deroul_ba(self) : return self.deroul_ba
	def get_en_exter(self) : return self.en_exter
	def get_en_inter(self) : return self.en_inter
	def get_eval_ba(self) : return self.eval_ba
	def get_nbre_pers_pres_ba(self) : return self.nbre_pers_pres_ba
	def get_outil_ba(self) : return self.outil_ba
	def get_photo_1_ba(self) : return self.photo_1_ba
	def get_photo_2_ba(self) : return self.photo_2_ba
	def get_photo_3_ba(self) : return self.photo_3_ba
	def get_plaq(self) : return self.plaq
	def get_rdp_1_ba(self) : return self.rdp_1_ba
	def get_rdp_2_ba(self) : return self.rdp_2_ba
	def get_rdp_3_ba(self) : return self.rdp_3_ba
	def get_themat_abord_ba(self) : return self.themat_abord_ba
	def get_titre_ba(self) : return self.titre_ba

	# Autres getters
	def get_bilan(self) : return self.id_bilan
	def get_pd(self) : return self.tplaquettesdistribuees_set
	def get_point(self) : return self.tpoint_set

	# Méthodes
	def get_attrs_ba(self, _pdf = False) :

		# Imports
		from app.functions.attributes_init import sub as attributes_init
		from app.functions.transform_bool import sub as transform_bool

		attrs_ba = self.get_attrs_bilan(_pdf, True)
		attrs_ba['deroul_ba'] = { 'label' : 'Déroulement de l\'animation', 'value' : self.get_deroul_ba() }
		attrs_ba['en_exter'] = {
			'label' : 'Y a-t-il eu des activités en extérieur ?', 'value' : transform_bool(self.get_en_exter())
		}
		attrs_ba['en_inter'] = {
			'label' : 'Y a-t-il eu des activités en intérieur ?', 'value' : transform_bool(self.get_en_inter())
		}
		attrs_ba['eval_ba'] = { 'label' : 'Évaluation de l\'animation', 'value' : self.get_eval_ba() }
		attrs_ba['nbre_pers_pres_ba'] = {
			'label' : 'Nombre de personnes présentes à l\'animation', 'value' : self.get_nbre_pers_pres_ba()
		}
		attrs_ba['outil_ba'] = {
			'download' : True,
			'label' : 'Télécharger l\'outil créé spécialement pour l\'animation',
			'value' : self.get_outil_ba__href()
		}
		attrs_ba['photo_ba'] = {
			'label' : 'Photo(s) de l\'animation',
			'row' : True,
			'value' : self.get_photo_ba__img_list({ 'style' : 'width: 100%;' })
		}
		attrs_ba['plaq'] = {
			'label' : 'Plaquette(s) distribuée(s)',
			'value' : [[
				elem.get_plaq__a_img({ 'target' : 'blank', 'title' : 'Afficher la plaquette' }, { 'height' : 40 }),
				elem.get_int_plaq()
			] for elem in self.get_plaq().all()],
			'table' : True,
			'table_header' : [[['Aperçu de la plaquette', None], ['Intitulé de la plaquette', None]]]
		}
		attrs_ba['point'] = {
			'label' : 'Point(s) positif(s)/négatif(s) de l\'animation',
			'value' : [[
				elem.get_int_point(),
				elem.get_comm_pos_point() or '-',
				elem.get_comm_neg_point() or '-'
			] for elem in self.get_point().all()],
			'table' : True,
			'table_header' : [
				[['Intitulé de l\'action', 'rowspan:2'], ['Commentaire', 'colspan:2']],
				[['Positif', None], ['Négatif', None]]
			]
		}
		attrs_ba['rdp_1_ba'] = {
			'label' : 'Consulter la revue de presse 1 de l\'animation',
			'pdf' : True,
			'value' : self.get_rdp_1_ba__href()
		}
		attrs_ba['rdp_2_ba'] = {
			'label' : 'Consulter la revue de presse 2 de l\'animation',
			'pdf' : True,
			'value' : self.get_rdp_2_ba__href()
		}
		attrs_ba['rdp_3_ba'] = {
			'label' : 'Consulter la revue de presse 3 de l\'animation',
			'pdf' : True,
			'value' : self.get_rdp_3_ba__href()
		}
		attrs_ba['themat_abord_ba'] = { 'label' : 'Thématiques abordées', 'value' : self.get_themat_abord_ba() }
		attrs_ba['titre_ba'] = { 'label' : 'Titre de l\'animation', 'value' : self.get_titre_ba() }

		return attributes_init(attrs_ba, _pdf)

	def get_outil_ba__href(self) :
		from django.conf import settings
		return '{}{}'.format(settings.MEDIA_URL, self.get_outil_ba()) if self.get_outil_ba() else None
	def get_photo_ba__img_list(self, _kwargs = {}) :

		# Import
		from django.conf import settings

		output = []

		# Stockage des chemins
		paths = [elem for elem in [self.get_photo_1_ba(), self.get_photo_2_ba(), self.get_photo_3_ba()] if elem]

		# Initialisation des arguments
		kwargs = {}
		for cle, val in _kwargs.items() : kwargs[cle] = val

		for p in paths :

			# Surchargement des arguments
			kwargs['src'] = '{}{}'.format(settings.MEDIA_URL, p)

			# Empilement des photos
			output.append('<img {}/>'.format(' '.join(['{}="{}"'.format(cle, val) for cle, val in kwargs.items()])))

		return output

	def get_rdp_1_ba__href(self) :
		from django.conf import settings
		return '{}{}'.format(settings.MEDIA_URL, self.get_rdp_1_ba()) if self.get_rdp_1_ba() else None
	def get_rdp_2_ba__href(self) :
		from django.conf import settings
		return '{}{}'.format(settings.MEDIA_URL, self.get_rdp_2_ba()) if self.get_rdp_2_ba() else None
	def get_rdp_3_ba__href(self) :
		from django.conf import settings
		return '{}{}'.format(settings.MEDIA_URL, self.get_rdp_3_ba()) if self.get_rdp_3_ba() else None

	def __str__(self) : return self.get_bilan()

class TPlaquettesDistribuees(models.Model) :

	# Attributs
	id_ba = models.ForeignKey(TBilanAnimation, on_delete = models.CASCADE)
	id_plaq = models.ForeignKey(TPlaquette, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_plaquettes_distribuees'
		verbose_name = verbose_name_plural = 'T_PLAQUETTES_DISTRIBUEES'

	# Getters
	def get_pk(self) : return self.pk
	def get_ba(self) : return self.id_ba
	def get_plaq(self) : return self.id_plaq

	def __str__(self) :
		return '{} - {}'.format(self.get_ba().get_anim(), self.get_plaq())

class TPoint(models.Model) :

	# Attributs
	id_point = models.AutoField(primary_key = True)
	comm_neg_point = models.TextField(blank = True, null = True, verbose_name = 'Commentaire négatif')
	comm_pos_point = models.TextField(blank = True, null = True, verbose_name = 'Commentaire positif')
	int_point = models.CharField(max_length = 255, verbose_name = 'Intitulé')
	id_ba = models.ForeignKey(TBilanAnimation, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_point'
		ordering = ['int_point']
		verbose_name = verbose_name_plural = 'T_POINT'

	# Getters
	def get_pk(self) : return self.pk
	def get_comm_neg_point(self) : return self.comm_neg_point
	def get_comm_pos_point(self) : return self.comm_pos_point
	def get_int_point(self) : return self.int_point
	def get_ba(self) : return self.id_ba

	def __str__(self) : return 'TODO'

class TOutil(models.Model) :

	# Méthode liée aux attributs
	def set_photo_outil__upload_to(_inst, _fn) :
		from app.functions.gen_string import sub; return 'outils/{}.{}'.format(sub(), _fn.split('.')[-1])

	# Attributs
	id_outil = models.AutoField(primary_key = True)
	descr_outil = models.TextField(blank = True, null = True, verbose_name = 'Description de l\'outil')
	int_outil = models.CharField(max_length = 255, verbose_name = 'Intitulé de l\'outil')
	photo_outil = models.ImageField(upload_to = set_photo_outil__upload_to, verbose_name = 'Aperçu de l\'outil')

	class Meta :
		db_table = 't_outil'
		ordering = ['int_outil']
		verbose_name = verbose_name_plural = 'T_OUTIL'

	# Getters
	def get_pk(self) : return self.pk
	def get_descr_outil(self) : return self.descr_outil
	def get_int_outil(self) : return self.int_outil
	def get_photo_outil(self) : return self.photo_outil

	# Autres getters
	def get_reserv(self) : return self.treservation_set

	# Méthode
	def get_photo_outil__img(self, _kwargs = {}) :

		# Import
		from django.conf import settings

		# Initialisation des arguments
		kwargs = {}
		for cle, val in  _kwargs.items() : kwargs[cle] = val
		kwargs['src'] = '{}{}'.format(settings.MEDIA_URL, self.get_photo_outil())

		return '<img {}/>'.format(' '.join(['{}="{}"'.format(cle, val) for cle, val in kwargs.items()]))

	def __str__(self) : return self.get_int_outil()

	def delete(self, *args, **kwargs) : self.get_photo_outil().delete(); super(TOutil, self).delete(*args, **kwargs)

class TReservation(models.Model) :

	# Imports
	from django.contrib.postgres.fields import ArrayField
	from django.core.validators import RegexValidator

	# Attributs
	id_reserv = models.AutoField(primary_key = True)
	borne_dt_reserv = ArrayField(base_field = models.CharField(max_length = 2), size = 2)
	comm_reserv = models.TextField(blank = True, null = True, verbose_name = 'Commentaire')
	courr_refer_reserv = models.EmailField(blank = True, null = True, verbose_name = 'Courriel du contact référent')
	doit_chercher = models.BooleanField(default = False, verbose_name = 'Le SMMAR doit-il chercher l\'outil ?')
	doit_demonter = models.BooleanField(default = False, verbose_name = 'Le SMMAR doit-il démonter l\'outil ?')
	doit_livrer = models.BooleanField(default = False, verbose_name = 'Le SMMAR doit-il livrer l\'outil ?')
	doit_monter = models.BooleanField(default = False, verbose_name = 'Le SMMAR doit-il monter l\'outil ?')
	dt_emiss_reserv = models.DateTimeField(auto_now_add = True)
	dt_reserv = ArrayField(base_field = models.DateField(), size = 2)
	nom_refer_reserv = models.CharField(max_length = 255, verbose_name = 'Nom de famille du contact référent')
	ou_chercher = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Où ?')
	ou_demonter = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Où ?')
	ou_livrer = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Où ?')
	ou_monter = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Où ?')
	prenom_refer_reserv = models.CharField(
		blank = True, max_length = 255, null = True, verbose_name = 'Prénom du contact référent'
	)
	quand_chercher = models.DateTimeField(
		blank = True, null = True, verbose_name = 'Quand ? <span class="fl-complement">(JJ/MM/AAAA HH:MM)</span>'
	)
	quand_demonter = models.DateTimeField(
		blank = True, null = True, verbose_name = 'Quand ? <span class="fl-complement">(JJ/MM/AAAA HH:MM)</span>'
	)
	quand_livrer = models.DateTimeField(
		blank = True, null = True, verbose_name = 'Quand ? <span class="fl-complement">(JJ/MM/AAAA HH:MM)</span>'
	)
	quand_monter = models.DateTimeField(
		blank = True, null = True, verbose_name = 'Quand ? <span class="fl-complement">(JJ/MM/AAAA HH:MM)</span>'
	)
	tel_refer_reserv = models.CharField(
		blank = True,
		max_length = 10,
		null = True, 
		validators = [RegexValidator(r'^[0-9]{10}')],
		verbose_name = 'Numéro de téléphone du contact référent'
	)
	id_outil = models.ForeignKey(TOutil, on_delete = models.CASCADE, verbose_name = 'Outil')
	id_util = models.ForeignKey(TUtilisateur, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_reservation'
		verbose_name = verbose_name_plural = 'T_RESERVATION'

	def clean(self) :

		# Imports
		from django.core.exceptions import ValidationError
		from smmaranim.custom_settings import ERROR_MESSAGES

		# Renvoi d'une erreur si aucune adresse électronique et aucun numéro de téléphone
		if self.get_nom_refer_reserv() :
			if not self.get_courr_refer_reserv() and not self.get_tel_refer_reserv() :
				raise ValidationError({ '__all__' : ERROR_MESSAGES['email_or_phone_number'] })

	# Getters
	def get_pk(self) : return self.pk
	def get_borne_dt_reserv(self) : return self.borne_dt_reserv
	def get_comm_reserv(self) : return self.comm_reserv
	def get_courr_refer_reserv(self) : return self.courr_refer_reserv
	def get_doit_chercher(self) : return self.doit_chercher
	def get_doit_demonter(self) : return self.doit_demonter
	def get_doit_livrer(self) : return self.doit_livrer
	def get_doit_monter(self) : return self.doit_monter
	def get_dt_emiss_reserv(self) : return self.dt_emiss_reserv
	def get_dt_reserv(self) : return self.dt_reserv
	def get_nom_refer_reserv(self) : return self.nom_refer_reserv
	def get_ou_chercher(self) : return self.ou_chercher
	def get_ou_demonter(self) : return self.ou_demonter
	def get_ou_livrer(self) : return self.ou_livrer
	def get_ou_monter(self) : return self.ou_monter
	def get_prenom_refer_reserv(self) : return self.prenom_refer_reserv
	def get_quand_chercher(self) : return self.quand_chercher
	def get_quand_demonter(self) : return self.quand_demonter
	def get_quand_livrer(self) : return self.quand_livrer
	def get_quand_monter(self) : return self.quand_monter
	def get_tel_refer_reserv(self) : return self.tel_refer_reserv
	def get_outil(self) : return self.id_outil
	def get_util(self) : return self.id_util

	# Autres getters
	def get_expos(self) : return self.texposition_set
	def get_rr(self) : return self.treferentreservation_set

	# Méthodes
	def get_attrs_reserv(self, _pdf = False) :

		# Import
		from app.functions.attributes_init import sub

		# Initialisation du tableau des aides proposées par le SMMAR
		aides = [[
			self.get_doit_livrer(),
			'Doit livrer l\'outil',
			self.get_quand_livrer__str(),
			self.get_ou_livrer()
		], [
			self.get_doit_monter(),
			'Doit monter l\'outil',
			self.get_quand_monter__str(),
			self.get_ou_monter()
		], [
			self.get_doit_chercher(),
			'Doit chercher l\'outil',
			self.get_quand_chercher__str(),
			self.get_ou_chercher()
		], [
			self.get_doit_demonter(),
			'Doit démonter l\'outil',
			self.get_quand_demonter__str(),
			self.get_ou_demonter()
		]]

		# Initialisation des attributs de la réservation
		attrs = {
			'aides' : {
				'label' : 'Action(s)',
				'value' : [elem[1:] for elem in aides if elem[0] == True],
				'table' : True,
				'table_header' : [[
					['Intitulé de l\'action', None],
					['Quand ?', None],
					['Où ?', None]
				]]
			},
			'comm_reserv' : { 'label' : 'Commentaire', 'value' : self.get_comm_reserv() },
			'courr_refer_reserv' : {
				'label' : 'Courriel de la personne référente', 'value' : self.get_courr_refer_reserv()
			},
			'dt_reserv' : { 'label' : 'Date(s) de réservation', 'value' : self.get_dt_reserv__fr_str() },
			'nom_complet_refer_reserv' : {
				'label' : 'Nom complet du contact référent', 'value' : self.get_nom_complet()
			},
			'org' : { 'label' : 'Organisme', 'value' : self.get_util().get_org() },
			'outil' : { 'label' : 'Outil', 'value' : self.get_outil() },
			'tel_refer_reserv' : {
				'label' : 'Numéro de téléphone de la personne référente',
				'value' : self.get_tel_refer_reserv__deconstructed()
			},
			'util' : {
				'label' : 'Utilisateur ayant effectué la dernière modification',
				'value' : self.get_util().get_nom_complet()
			}
		}

		return sub(attrs, _pdf)

	def get_dt_reserv__str(self) :
		from app.functions.get_local_format import sub; return [sub(elem) for elem in self.get_dt_reserv()]
	def get_dt_reserv__fr_str(self) :

		donnees = []

		# Définition des bornes traduites
		bornes = { 'AM' : 'matin', 'PM' : 'après-midi', 'WD' : 'journée entière' }

		# Préparation des données concernant la/les date(s) de réservation
		for i in range(len(self.get_dt_reserv__str())) :
			donnees.append('{} ({})'.format(self.get_dt_reserv__str()[i], bornes[self.get_borne_dt_reserv()[i]]))

		return ' - '.join(donnees)
	def get_nom_complet(self) :
		return '{} {}'.format(self.get_nom_refer_reserv(), self.get_prenom_refer_reserv())
	def get_quand_chercher__str(self) :
		from app.functions.get_local_format import sub
		return sub(self.get_quand_chercher()) if self.get_quand_chercher() else None
	def get_quand_demonter__str(self) :
		from app.functions.get_local_format import sub
		return sub(self.get_quand_demonter()) if self.get_quand_demonter() else None
	def get_quand_livrer__str(self) :
		from app.functions.get_local_format import sub
		return sub(self.get_quand_livrer()) if self.get_quand_livrer() else None
	def get_quand_monter__str(self) :
		from app.functions.get_local_format import sub
		return sub(self.get_quand_monter()) if self.get_quand_monter() else None
	def get_tel_refer_reserv__deconstructed(self) :
		t = iter(self.get_tel_refer_reserv()); return '-'.join(a + b for a, b in zip(t, t))

	def __str__(self) :
		return '{} - {} - {}'.format(self.get_nom_complet(), self.get_outil(), self.get_dt_reserv__fr_str())

class TReferentReservation(models.Model) :

	# Import
	from django.core.validators import RegexValidator

	# Attributs
	id_rr = models.AutoField(primary_key = True)
	courr_rr = models.EmailField(blank = True, null = True, verbose_name = 'Courriel du contact référent')
	est_princ = models.BooleanField(default = False)
	nom_rr = models.CharField(max_length = 255, verbose_name = 'Nom de famille du contact référent')
	prenom_rr = models.CharField(
		blank = True, max_length = 255, null = True, verbose_name = 'Prénom du contact référent'
	)
	tel_rr = models.CharField(
		blank = True,
		max_length = 10,
		null = True,
		validators = [RegexValidator(r'^[0-9]{10}')],
		verbose_name = 'Numéro de téléphone du contact référent'
	)
	id_reserv = models.ForeignKey(TReservation, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_referent_reservation'
		ordering = ['nom_rr', 'prenom_rr']
		verbose_name = verbose_name_plural = 'T_REFERENT_RESERVATION'

	def clean(self) :

		# Imports
		from django.core.exceptions import ValidationError
		from smmaranim.custom_settings import ERROR_MESSAGES

		# Renvoi d'une erreur si aucune adresse électronique et aucun numéro de téléphone
		if self.get_nom_rr() :
			if not self.get_courr_rr() and not self.get_tel_rr() :
				raise ValidationError({ '__all__' : ERROR_MESSAGES['email_or_phone_number'] })

	# Getters
	def get_pk(self) : return self.pk
	def get_courr_rr(self) : return self.courr_rr
	def get_nom_rr(self) : return self.nom_rr
	def get_prenom_rr(self) : return self.prenom_rr
	def get_reserv(self) : return self.id_reserv
	def get_tel_rr(self) : return self.tel_rr

	# Autres getters
	def get_expos(self) : return self.texposition_set

	# Méthodes
	def get_expos__count(self) : return self.get_expos().count()
	def get_nom_complet(self) : return '{} {}'.format(self.get_nom_rr(), self.get_prenom_rr())
	def get_tel_rr__deconstructed(self) : t = iter(self.get_tel_rr()); return '-'.join(a + b for a, b in zip(t, t))

	def __str__(self) : return self.get_nom_complet()

class TExposition(models.Model) :

	# Imports
	from django.contrib.postgres.fields import ArrayField
	from django.core.validators import RegexValidator

	# Attributs
	id_expos = models.AutoField(primary_key = True)
	borne_dt_expos = ArrayField(base_field = models.CharField(max_length = 2), size = 2)
	comm_expos = models.TextField(blank = True, null = True, verbose_name = 'Commentaire')
	dt_expos = ArrayField(base_field = models.DateField(), size = 2)
	lieu_expos = models.CharField(max_length = 255, verbose_name = 'Lieu d\'exposition')
	code_comm = models.ForeignKey(TCommune, on_delete = models.CASCADE)
	id_reserv = models.ForeignKey(TReservation, on_delete = models.CASCADE)
	id_rr = models.ForeignKey(TReferentReservation, on_delete = models.CASCADE)
	id_struct = models.ForeignKey(TStructure, on_delete = models.CASCADE, verbose_name = 'Structure d\'accueil')

	class Meta :
		db_table = 't_exposition'
		ordering = ['dt_expos']
		verbose_name = verbose_name_plural = 'T_EXPOSITION'

	# Getters
	def get_pk(self) : return self.pk
	def get_borne_dt_expos(self) : return self.borne_dt_expos
	def get_comm_expos(self) : return self.comm_expos
	def get_dt_expos(self) : return self.dt_expos
	def get_lieu_expos(self) : return self.lieu_expos
	def get_comm(self) : return self.code_comm
	def get_reserv(self) : return self.id_reserv
	def get_rr(self) : return self.id_rr
	def get_struct(self) : return self.id_struct

	# Méthodes
	def get_dt_expos__str(self) :
		from app.functions.get_local_format import sub; return [sub(elem) for elem in self.get_dt_expos()]
	def get_dt_expos__fr_str(self) :

		donnees = []

		# Définition des bornes traduites
		bornes = { 'AM' : 'matin', 'PM' : 'après-midi', 'WD' : 'journée entière' }

		# Préparation des données concernant la/les date(s) de réservation
		for i in range(len(self.get_dt_expos__str())) :
			donnees.append('{} ({})'.format(self.get_dt_expos__str()[i], bornes[self.get_borne_dt_expos()[i]]))

		return ' - '.join(donnees)

	def __str__(self) :
		return '{} - {} - {}'.format(self.get_lieu_expos(), self.get_comm(), self.get_dt_expos__fr_str())