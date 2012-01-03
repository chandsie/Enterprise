from django import forms
from django.contrib.auth.models import User
from django.forms.extras.widgets import SelectDateWidget
from django.forms.models import ModelChoiceField
import datetime
import re

class EmployeeChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.last_name + ", " + obj.first_name

class LogForm(forms.Form):
    username = EmployeeChoiceField(
                                   queryset=User.objects.all().exclude(username=u'admin').order_by('last_name'),
                                   label = u'Name',
                                   error_messages={'required':'Please select your name!'}
                                   )
    password = forms.CharField(
                               label=u'Password',
                               widget=forms.PasswordInput(),
                               error_messages={'required':'Please enter your password!'}
                               )
    
    def clean(self):
        data = self.cleaned_data
        user = data.get('username')
        pwd = data.get('password')
        if user and pwd:
            if not user.check_password(pwd):
                raise forms.ValidationError("The given username and password do not match!")
        return data


class PasswordUpdateForm(forms.Form):
    username = EmployeeChoiceField(
                               queryset=User.objects.all().exclude(username=u'admin').order_by('last_name'),
                               label = u'Name',
                               error_messages={'required':'Please select your name!'}
                               )
    curPassword = forms.CharField(
                               label=u'Current Password',
                               widget=forms.PasswordInput(),
                               error_messages={'required':'Please enter your current password!'}
                               )
    
    newPassword = forms.CharField(
                               label=u'New Password',
                               widget=forms.PasswordInput(),
                               error_messages={'required':'Please enter a password!'}
                               )
    
    newPassword2 = forms.CharField(
                               label=u'New Password (Again)',
                               widget=forms.PasswordInput(),
                               error_messages={'required':'Please retype your password!'}
                               )
    
    def clean_newPassword2(self):
        if 'newPassword' in self.cleaned_data:
            p1 = self.cleaned_data['newPassword']
            p2 = self.cleaned_data['newPassword2']
            if p1 == p2:
                return p2
        raise forms.ValidationError('Passwords do not match!')
    
    def clean(self):
        data = self.cleaned_data
        user = data.get('username')
        pwd = data.get('curPassword')
        
        if user and pwd:
            if not user.check_password(pwd):
                raise forms.ValidationError("The given username and password do not match!")
        return data

class AdminLoginForm(forms.Form):
    password = forms.CharField(
                               label=u'Password',
                               widget=forms.PasswordInput(),
                               error_messages={'required':'Please enter the password!'}
                               )
    
    def clean_password(self):
        password = self.cleaned_data['password']
        if not User.objects.get(username=u'admin').check_password(password):
            raise forms.ValidationError('The password you entered is incorrect!')
        return password
        
    
class RegistrationForm(forms.Form):
    firstName = forms.CharField(
                                label=u'First Name',
                                max_length=20,
                                error_messages={'required':'Please enter your first name!'}
                                )
    lastName = forms.CharField(
                               label=u'Last Name',
                               max_length=20,
                               error_messages={'required':'Please enter your first name!'}
                               )
       
    def clean(self):
        first = self.cleaned_data.get('firstName')
        last = self.cleaned_data.get('lastName')
        
        try:
            User.objects.get(first_name=first, last_name=last)
            raise forms.ValidationError("An account with that name already exists!")
        except User.DoesNotExist:
            pass
                    
        return self.cleaned_data
    
    
    def clean_firstName(self):
        return self._clean_name(self.cleaned_data['firstName'])
    def clean_lastName(self):
        return self._clean_name(self.cleaned_data['lastName'])
    
    def _clean_name(self, name):
        if not re.search(r'^[a-zA-Z\-\']+$', name):
            raise forms.ValidationError('A name can only contain letters, dashes and apostrophes.')
        return name

class RangeReportForm(forms.Form):
    begin = forms.DateField(
                            label=u'Beginning Date',
                            widget=SelectDateWidget(years = [datetime.date.today().year - i for i in range(10)]),
                            initial=datetime.date.today()-datetime.timedelta(days=14)
                            )
    end = forms.DateField(
                          label=u'Ending Date',
                          widget=SelectDateWidget(years = [datetime.date.today().year - i for i in range(10)]),
                          initial=datetime.date.today()
                          )

    def clean(self):
        data = self.cleaned_data
        begin = data.get('begin')
        end = data.get('end')
        if end and begin:
            if end < begin:
                raise forms.ValidationError('The end date cannot be before the begin date!')
        
        return data
