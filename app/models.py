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
		verbose_name = verbose_name_plural = 'T_TYPE_UTILISATEUR'

	# Getters
	def get_pk(self) : return self.pk
	def get_int_type_util(self) : return self.int_type_util

	def __str__(self) : return self.get_int_type_util()

class TOrganisme(models.Model) :

	# Attributs
	id_org = models.AutoField(primary_key = True)
	coul_org = models.CharField(default = 'revert', max_length = 255, verbose_name = 'Couleur HTML hexadécimale')
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
		import re

		# Renvoi d'une erreur en cas de renseignement d'une couleur inexistante
		if self.get_coul_org() != 'revert' :
			if not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', self.get_coul_org()) :
				raise ValidationError({ 'coul_org' : '' })

class TUtilisateur(User) :

	# Attribut
	en_mode_superadmin = models.BooleanField(default = False)
	id_org = models.ForeignKey(TOrganisme, on_delete = models.CASCADE, verbose_name = 'Organisme')

	# Relation
	type_util = models.ManyToManyField(TTypeUtilisateur, through = 'TDroitsUtilisateur')

	class Meta :
		db_table = 't_utilisateur'
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
	def get_is_superadmin(self) : return True if self.get_is_staff() and self.get_is_superuser() else False

	def get_menu(self) :

		# Import
		from smmaranim.custom_settings import MENU

		output = {}

		# Définition des modules accessibles par l'utilisateur
		for cle, val in MENU.items() :
			if set(self.get_type_util__list()).intersection(val['mod_rights']) : output[cle] = val

		# Tri des modules par ordre d'affichage
		output = dict(sorted(output.items(), key = lambda l : l[1]['mod_rank']))

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
		validators = [MinValueValidator(0.5), valid_dj],
		verbose_name = 'Nombre de demi-journées pour les animations ponctuelles'
	)
	nbre_dj_pp_pm = models.FloatField(
		validators = [MinValueValidator(0.5), valid_dj],
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
	def get_tdj(self) : return self.ttransactiondemijournees_set

	# Méthodes
	def get_nbre_dj_ap_pm__str(self) : return '{0:g}'.format(self.get_nbre_dj_ap_pm())
	def get_nbre_dj_pp_pm__str(self) : return '{0:g}'.format(self.get_nbre_dj_pp_pm())

	def __str__(self) : return '{} - {}'.format(self.get_prest(), self.get_marche())

class TTransactionDemiJournees(models.Model) :

	# Imports
	from app.validators import valid_dj
	from django.core.validators import MinValueValidator

	# Attributs
	id_tdj = models.AutoField(primary_key = True)
	int_tdj = models.CharField(max_length = 255, verbose_name = 'Intitulé')
	nbre_dj_tdj = models.FloatField(
		validators = [MinValueValidator(0.5), valid_dj], verbose_name = 'Nombre de demi-journées'
	)
	id_pm = models.ForeignKey(TPrestatairesMarche, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_transaction_demi_journees'
		verbose_name = verbose_name_plural = 'T_TRANSACTION_DEMI_JOURNEES'

	# Getters
	def get_pk(self) : return self.pk
	def get_int_tdj(self) : return self.int_tdj
	def get_nbre_dj_tdj(self) : return self.nbre_dj_tdj
	def get_pm(self) : return self.id_pm

	# Méthode
	def get_nbre_dj_tdj__str(self) : return '{0:g}'.format(self.get_nbre_dj_tdj())

	def __str__(self) :
		return '{} - {} ({} demi-journée(s))'.format(self.get_pm(), self.get_int_tdj(), self.get_nbre_dj_tdj__str())

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
	nom_ecole = models.CharField(max_length = 255, verbose_name = 'Nom de l\'école')
	code_comm = models.ForeignKey(TCommune, on_delete = models.CASCADE, verbose_name = 'Commune')

	class Meta :
		db_table = 't_ecole'
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

	# Attributs
	id_projet = models.AutoField(primary_key = True)
	comm_projet = models.TextField(blank = True, null = True, verbose_name = 'Commentaire')
	int_projet = models.CharField(max_length = 255, verbose_name = 'Intitulé du projet')
	id_org = models.ForeignKey(TOrganisme, on_delete = models.CASCADE)
	id_pm = models.ForeignKey(TPrestatairesMarche, null = True, on_delete = models.CASCADE)
	id_sti = models.ForeignKey(TSousTypeIntervention, null = True, on_delete = models.CASCADE)
	id_type_public = models.ForeignKey(TTypePublic, on_delete = models.CASCADE, verbose_name = 'Type de public visé')

	class Meta :
		db_table = 't_projet'
		ordering = ['int_projet']
		verbose_name = verbose_name_plural = 'T_PROJET'

	# Getters
	def get_pk(self) : return self.pk
	def get_comm_projet(self) : return self.comm_projet
	def get_int_projet(self) : return self.int_projet
	def get_org(self) : return self.id_org
	def get_pm(self) : return self.id_pm
	def get_sti(self) : return self.id_sti
	def get_type_public(self) : return self.id_type_public

	# Autres getters
	def get_cep(self) : return self.tclassesecoleprojet_set

	# Méthodes
	def get_attrs_projet(self, _pdf = False) :

		# Import
		from app.functions.attributes_init import sub

		# Initialisation des attributs du projet
		attrs = {
			'comm_projet' : { 'label' : 'Commentaire', 'value' : self.get_comm_projet() },
			'int_projet' : { 'label' : 'Intitulé du projet', 'value' : self.get_int_projet() },
			'marche' : { 'label' : 'Marché', 'value' : self.get_pm().get_marche() if self.get_pm() else None },
			'org' : { 'label' : 'Organisme', 'value' : self.get_org() },
			'sti' : { 'label' : 'Événement', 'value' : self.get_sti() },
			'type_interv' : { 'label' : 'Type d\'intervention', 'value' : self.get_type_interv() },
			'type_public' : { 'label' : 'Type de public visé', 'value' : self.get_type_public() }
		}

		return sub(attrs, _pdf)

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
	courr_refer_cep = models.EmailField(verbose_name = 'Courriel du contact référent')
	nom_refer_cep = models.CharField(max_length = 255, verbose_name = 'Nom de famille du contact référent')
	prenom_refer_cep = models.CharField(max_length = 255, verbose_name = 'Prénom du contact référent')
	tel_refer_cep = models.CharField(
		max_length = 10,
		validators = [RegexValidator(r'^[0-9]{10}')],
		verbose_name = 'Numéro de téléphone du contact référent'
	)

	class Meta :
		db_table = 't_classes_ecole_projet'
		verbose_name = verbose_name_plural = 'T_CLASSES_ECOLE_PROJET'

	# Getters
	def get_pk(self) : return self.pk
	def get_classe(self) : return self.id_classe
	def get_ecole(self) : return self.id_ecole
	def get_projet(self) : return self.id_projet
	def get_courr_refer_cep(self) : return self.courr_refer_cep
	def get_nom_refer_cep(self) : return self.nom_refer_cep
	def get_prenom_refer_cep(self) : return self.prenom_refer_cep
	def get_tel_refer_cep(self) : return self.tel_refer_cep

	# Méthodes
	def get_attrs_cep(self, _pdf = False) :

		# Import
		from app.functions.attributes_init import sub

		# Initialisation des attributs de la classe
		attrs = {
			'courr_refer_cep' : { 'label' : 'Courriel du contact référent', 'value' : self.get_courr_refer_cep() },
			'id_classe' : { 'label' : 'Classe', 'value' : self.get_classe() },
			'id_ecole' : { 'label' : 'Établissement scolaire', 'value' : self.get_ecole() },
			'refer_cep' : { 'label' : 'Nom complet du contact référent', 'value' : self.get_nom_complet() },
			'tel_refer_cep' : {
				'label' : 'Numéro de téléphone du contact référent', 'value' : self.get_tel_refer_cep__deconstructed()
			}
		}

		return sub(attrs, _pdf)

	def get_nom_complet(self) : return '{} {}'.format(self.get_nom_refer_cep(), self.get_prenom_refer_cep())
	def get_tel_refer_cep__deconstructed(self) :
		t = iter(self.get_tel_refer_cep()); return '-'.join(a + b for a, b in zip(t, t))

	def __str__(self) : return '{} - {} - {}'.format(self.get_projet(), self.get_classe(), self.get_ecole())

class TAnimation(models.Model) :

	# Imports
	from django.contrib.postgres.fields import ArrayField
	from smmaranim.custom_settings import HALF_DAY_CHOICES

	# Attributs
	id_anim = models.AutoField(primary_key = True)
	dt_anim = models.DateField()
	est_anim = models.BooleanField()
	heure_anim = ArrayField(base_field = models.TimeField(), size = 2)
	lieu_anim = models.CharField(max_length = 255)
	nbre_dj_anim = models.FloatField(choices = [(elem, str(elem)) for elem in HALF_DAY_CHOICES])
	num_anim = models.PositiveIntegerField(blank = True, null = True)
	code_comm = models.ForeignKey(TCommune, on_delete = models.CASCADE)
	id_projet = models.ForeignKey(TProjet, on_delete = models.CASCADE)
	id_struct = models.ForeignKey(TStructure, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_animation'
		verbose_name = verbose_name_plural = 'T_ANIMATION'

	# Getters
	def get_pk(self) : return self.pk
	def get_comm(self) : return self.code_comm
	def get_dt_anim(self) : return self.dt_anim
	def get_est_anim(self) : return self.est_anim
	def get_heure_anim(self) : return self.heure_anim
	def get_lieu_anim(self) : return self.lieu_anim
	def get_nbre_dj_anim(self) : return self.nbre_dj_anim
	def get_num_anim(self) : return self.num_anim
	def get_projet(self) : return self.id_projet
	def get_struct(self) : return self.id_struct

	# Méthodes
	def get_est_anim__str(self) : return 'Anim' if self.get_est_anim() == True else 'RDV'
	def get_heure_anim__str(self) :
		from app.functions.get_local_format import sub; return [sub(elem)[1] for elem in self.get_heure_anim()]

	def __str__(self) : 
		return '{} : {} {} ({})'.format(
			'-'.join(self.get_heure_anim__str()),
			self.get_est_anim__str(),
			self.get_comm().get_nom_comm(),
			self.get_lieu_anim()
		)

class TBilan(models.Model) :

	# Attributs
	id_bilan = models.AutoField(primary_key = True)
	comm_bilan = models.TextField(blank = True, null = True)
	nbre_pers_pres_bilan = models.PositiveIntegerField()
	nbre_pers_prev_bilan = models.PositiveIntegerField(blank = True, null = True)
	id_anim = models.ForeignKey(TAnimation, on_delete = models.CASCADE)
	id_util = models.ForeignKey(TUtilisateur, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_bilan'
		verbose_name = verbose_name_plural = 'T_BILAN'

	# Getters
	def get_pk(self) : return self.pk
	def get_comm_bilan(self) : return self.comm_bilan
	def get_nbre_pers_pres_bilan(self) : return self.nbre_pers_pres_bilan
	def get_nbre_pers_prev_bilan(self) : return self.nbre_pers_prev_bilan
	def get_anim(self) : return self.id_anim
	def get_util(self) : return self.id_util

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
		verbose_name = verbose_name_plural = 'T_PLAQUETTE'

	# Getters
	def get_pk(self) : return self.pk
	def get_int_plaq(self) : return self.int_plaq
	def get_miniat_plaq(self) : return self.miniat_plaq
	def get_pdf_plaq(self) : return self.pdf_plaq

	# Méthode
	def get_plaq__a_img(self, _a_kwargs = {}, _img_kwargs = {}) :

		# Import
		from django.conf import settings

		# Initialisation des arguments
		a_kwargs = {}
		for cle, val in  _a_kwargs.items() : a_kwargs[cle] = val
		a_kwargs['href'] = '{}{}'.format(settings.MEDIA_URL, self.get_pdf_plaq())
		img_kwargs = {}
		for cle, val in  _img_kwargs.items() : img_kwargs[cle] = val
		img_kwargs['src'] = '{}{}'.format(settings.MEDIA_URL, self.get_miniat_plaq())

		return '<a {}><img {}/></a>'.format(
			' '.join(['{}="{}"'.format(cle, val) for cle, val in a_kwargs.items()]),
			' '.join(['{}="{}"'.format(cle, val) for cle, val in img_kwargs.items()])
		)

	def __str__(self) : return self.get_int_plaq()

	def delete(self, *args, **kwargs) :
		self.get_pdf_plaq().delete(); self.get_miniat_plaq().delete(); super(TPlaquette, self).delete(*args, **kwargs)

class TBilanAnimation(TBilan) :

	# Import
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
	deroul_ba = models.TextField(blank = True, null = True)
	en_exter = models.BooleanField()
	en_inter = models.BooleanField()
	eval_ba = models.CharField(choices = [(elem, elem) for elem in EVALUATION_CHOICES], max_length = 4)
	outil_ba = models.FileField(blank = True, null = True, upload_to = set_outil_ba__upload_to)
	photo_1_ba = models.ImageField(blank = True, null = True, upload_to = set_photo_ba__upload_to)
	photo_2_ba = models.ImageField(blank = True, null = True, upload_to = set_photo_ba__upload_to)
	photo_3_ba = models.ImageField(blank = True, null = True, upload_to = set_photo_ba__upload_to)
	rdp_1_ba = models.FileField(blank = True, null = True, upload_to = set_rdp_ba__upload_to)
	rdp_2_ba = models.FileField(blank = True, null = True, upload_to = set_rdp_ba__upload_to)
	rdp_3_ba = models.FileField(blank = True, null = True, upload_to = set_rdp_ba__upload_to)
	themat_abord_ba = models.TextField(blank = True, null = True)
	theme_ba = models.CharField(max_length = 255)
	titre_ba = models.CharField(blank = True, max_length = 255, null = True)

	# Relations
	cep = models.ManyToManyField(TClassesEcoleProjet, through = 'TElevesClasseEcoleProjet')
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
	def get_outil_ba(self) : return self.outil_ba
	def get_photo_1_ba(self) : return self.photo_1_ba
	def get_photo_2_ba(self) : return self.photo_2_ba
	def get_photo_3_ba(self) : return self.photo_3_ba
	def get_plaq(self) : return self.plaq
	def get_rdp_1_ba(self) : return self.rdp_1_ba
	def get_rdp_2_ba(self) : return self.rdp_2_ba
	def get_rdp_3_ba(self) : return self.rdp_3_ba
	def get_themat_abord_ba(self) : return self.themat_abord_ba
	def get_theme_ba(self) : return self.theme_ba
	def get_titre_ba(self) : return self.titre_ba

	def __str__(self) : return 'TODO'

class TElevesClasseEcoleProjet(models.Model) :

	# Attributs
	id_ba = models.ForeignKey(TBilanAnimation, on_delete = models.CASCADE)
	id_cep = models.ForeignKey(TClassesEcoleProjet, on_delete = models.CASCADE)
	nbre_eleves_pres_ecep = models.PositiveIntegerField()
	nbre_eleves_prev_ecep = models.PositiveIntegerField()

	class Meta :
		db_table = 't_eleves_classe_ecole_projet'
		verbose_name = verbose_name_plural = 'T_ELEVES_CLASSE_ECOLE_PROJET'

	# Getters
	def get_pk(self) : return self.pk
	def get_ba(self) : return self.id_ba
	def get_cep(self) : return self.id_cep
	def get_nbre_eleves_pres_ecep(self) : return self.nbre_eleves_pres_ecep
	def get_nbre_eleves_prev_ecep(self) : return self.nbre_eleves_prev_ecep

	def __str__(self) : return 'TODO'

class TPlaquettesDistribuees(models.Model) :

	# Attributs
	id_ba = models.ForeignKey(TBilanAnimation, on_delete = models.CASCADE)
	id_plaq = models.ForeignKey(TPlaquette, on_delete = models.CASCADE)
	nbre_plaq_distrib = models.PositiveIntegerField()

	class Meta :
		db_table = 't_plaquettes_distribuees'
		verbose_name = verbose_name_plural = 'T_PLAQUETTES_DISTRIBUEES'

	# Getters
	def get_pk(self) : return self.pk
	def get_ba(self) : return self.id_ba
	def get_plaq(self) : return self.id_plaq
	def get_nbre_plaq_distrib(self) : return self.nbre_plaq_distrib

	def __str__(self) :
		return '{} - {} ({} plaquette(s) distribuée(s))'.format(
			self.get_ba().get_anim(), self.get_plaq(), self.get_nbre_plaq_distrib()
		)

class TPoint(models.Model) :

	# Attributs
	id_point = models.AutoField(primary_key = True)
	comm_neg_point = models.TextField(blank = True, null = True)
	comm_pos_point = models.TextField(blank = True, null = True)
	int_point = models.CharField(max_length = 255)
	id_ba = models.ForeignKey(TBilanAnimation, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_point'
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

class TReservation(models.Model) :

	# Imports
	from django.contrib.postgres.fields import ArrayField
	from django.core.validators import RegexValidator

	# Attributs
	id_reserv = models.AutoField(primary_key = True)
	borne_dt_reserv = ArrayField(base_field = models.CharField(max_length = 2), size = 2)
	comm_reserv = models.TextField(blank = True, null = True, verbose_name = 'Commentaire')
	courr_refer_reserv = models.EmailField(verbose_name = 'Courriel du contact référent')
	doit_chercher = models.BooleanField(default = 0, verbose_name = 'Le SMMAR doit-il chercher l\'outil ?')
	doit_demonter = models.BooleanField(default = 0, verbose_name = 'Le SMMAR doit-il démonter l\'outil ?')
	doit_livrer = models.BooleanField(default = 0, verbose_name = 'Le SMMAR doit-il livrer l\'outil ?')
	doit_monter = models.BooleanField(default = 0, verbose_name = 'Le SMMAR doit-il monter l\'outil ?')
	dt_emiss_reserv = models.DateTimeField(auto_now_add = True)
	dt_reserv = ArrayField(base_field = models.DateField(), size = 2)
	nom_refer_reserv = models.CharField(max_length = 255, verbose_name = 'Nom de famille du contact référent')
	ou_chercher = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Où ?')
	ou_demonter = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Où ?')
	ou_livrer = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Où ?')
	ou_monter = models.CharField(blank = True, max_length = 255, null = True, verbose_name = 'Où ?')
	prenom_refer_reserv = models.CharField(max_length = 255, verbose_name = 'Prénom du contact référent')
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
		max_length = 10,
		validators = [RegexValidator(r'^[0-9]{10}')],
		verbose_name = 'Numéro de téléphone du contact référent'
	)
	id_outil = models.ForeignKey(TOutil, on_delete = models.CASCADE, verbose_name = 'Outil')
	id_util = models.ForeignKey(TUtilisateur, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_reservation'
		verbose_name = verbose_name_plural = 'T_RESERVATION'

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
				'label' : 'Nom complet de la personne référente', 'value' : self.get_nom_complet()
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
	courr_rr = models.EmailField(verbose_name = 'Courriel du contact référent')
	nom_rr = models.CharField(max_length = 255, verbose_name = 'Nom de famille du contact référent')
	prenom_rr = models.CharField(max_length = 255, verbose_name = 'Prénom du contact référent')
	tel_rr = models.CharField(
		max_length = 10,
		validators = [RegexValidator(r'^[0-9]{10}')],
		verbose_name = 'Numéro de téléphone du contact référent'
	)
	id_reserv = models.ForeignKey(TReservation, on_delete = models.CASCADE)

	class Meta :
		db_table = 't_referent_reservation'
		ordering = ['nom_rr', 'prenom_rr']
		verbose_name = verbose_name_plural = 'T_REFERENT_RESERVATION'

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