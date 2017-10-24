# coding: utf-8

# Imports
from app.models import *
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from smmaranim.custom_settings import EMPTY_VALUE

class FUtilisateurCreate(forms.ModelForm) :

    # Champs
    zs_password = forms.CharField(label = 'Mot de passe', widget = forms.PasswordInput())
    zs_password_bis = forms.CharField(label = 'Confirmation du mot de passe', widget = forms.PasswordInput())
    zl_type_util = forms.ModelMultipleChoiceField(
        label = 'Rôles de l\'utilisateur',
        queryset = TTypeUtilisateur.objects.all(),
        required = False,
        widget = FilteredSelectMultiple('T_TYPE_UTILISATEUR', is_stacked = False)
    )

    class Meta :
        fields = ['email', 'first_name', 'id_org', 'is_active', 'is_staff', 'is_superuser', 'last_name', 'username']
        labels = { 'email' : 'Courriel', 'last_name' : 'Nom de famille' }
        model = TUtilisateur

    def __init__(self, *args, **kwargs) :
        super(FUtilisateurCreate, self).__init__(*args, **kwargs)

        # Passage de certains champs à l'état requis
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def clean_zs_password_bis(self) :

        # Stockage des données du formulaire
        cleaned_data = self.cleaned_data
        val_password = cleaned_data.get('zs_password')
        val_password_bis = cleaned_data.get('zs_password_bis')

        # Renvoi d'une erreur si non-similitude des mots de passe
        if val_password and val_password_bis and val_password != val_password_bis :
            raise forms.ValidationError('Les mots de passe saisis ne correspondent pas.')

    def save(self, *args, **kwargs) :

        # Stockage des données du formulaire
        cleaned_data = self.cleaned_data
        val_password = cleaned_data.get('zs_password')
        val_type_util = cleaned_data.get('zl_type_util')

        # Création d'une instance TUtilisateur
        obj = super(FUtilisateurCreate, self).save(*args, **kwargs)
        obj.set_password(self.cleaned_data.get('zs_password'))
        obj.save()

        # Liaison avec la table t_droits_utilisateur
        obj.get_du().all().delete()
        for tu in val_type_util : TDroitsUtilisateur.objects.create(code_type_util = tu, id_util = obj)

        return obj

class FUtilisateurUpdate(forms.ModelForm) :

    # Import
    from django.contrib.auth.forms import ReadOnlyPasswordHashField

    # Champs
    password = ReadOnlyPasswordHashField(
        help_text = '''
        Les mots de passe ne sont pas enregistrés en clair, ce qui ne permet pas d'afficher le mot de passe de cet
        utilisateur, mais il est possible de le changer en utilisant <a href="../password/">ce formulaire</a>.
        ''',
        label = 'Mot de passe'
    )
    zl_type_util = forms.ModelMultipleChoiceField(
        label = 'Rôles de l\'utilisateur',
        queryset = TTypeUtilisateur.objects.all(),
        required = False,
        widget = FilteredSelectMultiple('T_TYPE_UTILISATEUR', is_stacked = False)
    )

    class Meta :
        fields = ['email', 'first_name', 'id_org', 'is_active', 'is_staff', 'is_superuser', 'last_name', 'username']
        labels = { 'email' : 'Courriel principal', 'last_name' : 'Nom de famille' }
        model = TUtilisateur

    def __init__(self, *args, **kwargs) :
        super(FUtilisateurUpdate, self).__init__(*args, **kwargs)

        # Passage de certains champs à l'état requis
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

        # Définition de la valeur initiale pour chaque champ
        self.fields['zl_type_util'].initial = [tu.get_pk() for tu in self.instance.get_type_util().all()]

    def clean_password(self) : return self.initial['password']

    def save(self, *args, **kwargs) :

        # Stockage des données du formulaire
        cleaned_data = self.cleaned_data
        val_type_util = cleaned_data.get('zl_type_util')

        # Modification d'une instance TUtilisateur
        obj = super(FUtilisateurUpdate, self).save(*args, **kwargs)
        obj.save()

        # Liaison avec la table t_droits_utilisateur
        obj.get_du().all().delete()
        for tu in val_type_util : TDroitsUtilisateur.objects.create(code_type_util = tu, id_util = obj)

        return obj

class FEcole(forms.ModelForm) :

    # Import
    from django.contrib.auth.forms import ReadOnlyPasswordHashField

    # Stockage des types d'établissments
    type_ecoles = ['ÉCOLE', 'COLLÈGE', 'LYCÉE', 'ÉTUDE SUPÉRIEURE']

    # Champs
    zl_type_ecole = forms.ChoiceField(
        choices = [EMPTY_VALUE] + [(elem, elem) for elem in type_ecoles],
        label = 'Type de l\'établissement',
        required = False
    )
    zs_nom_ecole = forms.CharField(label = 'Nom de l\'établissement')

    class Meta :
        fields = ['code_comm']
        model = TEcole

    def __init__(self, *args, **kwargs) :
        super(FEcole, self).__init__(*args, **kwargs)

        if self.instance.get_pk() :

            # Initialisation de la valeur de chaque champ (première phase)
            type_ecole = None
            nom_ecole = self.instance.get_nom_ecole()

            # Initialisation de la valeur de chaque champ (dernière phase)
            for te in [elem[0] for elem in self.fields['zl_type_ecole'].choices if elem[0]] :
                if nom_ecole.startswith(te) :
                    type_ecole = te
                    nom_ecole = nom_ecole.replace('{} '.format(te), '')
                    break

            # Définition de la valeur initiale pour chaque champ
            self.fields['zl_type_ecole'].initial = type_ecole
            self.fields['zs_nom_ecole'].initial = nom_ecole

    def save(self, *args, **kwargs) :

        # Stockage des données du formulaire
        cleaned_data = self.cleaned_data
        val_type_ecole = cleaned_data.get('zl_type_ecole')
        val_nom_ecole = cleaned_data.get('zs_nom_ecole')

        # Création/modification d'une instance TEcole
        obj = super(FEcole, self).save(*args, **kwargs)
        obj.nom_ecole = '{} {}'.format(val_type_ecole, val_nom_ecole) if val_type_ecole else val_nom_ecole
        obj.save()

        return obj