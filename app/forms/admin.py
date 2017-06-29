# coding: utf-8

# Imports
from app.models import *
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

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