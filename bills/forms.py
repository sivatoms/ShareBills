from django import forms

from .models import Transactions, GroupMembers,Group, Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.forms import models

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email')

class Member_SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone', 'birth_date')



class CustomModelChoiceIterator(models.ModelChoiceIterator):
    def choice(self, obj):
        return (self.field.prepare_value(obj),
                self.field.label_from_instance(obj), obj)

class CustomModelChoiceField(models.ModelMultipleChoiceField):
    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return CustomModelChoiceIterator(self)
    choices = property(_get_choices,
                       forms.MultipleChoiceField._set_choices)


class Bill_CreateForm(forms.Form):

    bill_type = forms.CharField(label='Bill type :', max_length=100, required=True)
    amount = forms.FloatField(label='Amount :', initial=0.00)


    def __init__(self, context, *args, **kwargs):
        super(Bill_CreateForm, self).__init__(*args, **kwargs)
        self.fields['share_with'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=tuple([(name.members.id, name) for name in context['users']]))

class Bill_EditForm(forms.ModelForm):

    def __init__(self, context, *args, **kwargs):
        super(Bill_EditForm, self).__init__(*args, **kwargs)
        self.fields['share_with'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=tuple([(name.members.id, name) for name in context['users']]))

    class Meta:
        model = Transactions
        fields = (
                    'bill_type',
                    'amount',
                    'share_with',
                )

class Group_CreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields=[
            'group_name',
        ]


class Add_new_members_form(forms.Form):
    member_email = forms.EmailField(required=True)
    class Meta:
        fields=[
            'member_email',
        ]
