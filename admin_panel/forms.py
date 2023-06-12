from django import forms
from django.contrib.auth import authenticate
from youonline_social_app.models import *

class ProiflePictureForm(forms.ModelForm):
    class Meta:
        model = ProfilePicture
        fields = "__all__"

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'last_name', 'mobile_number']
        widgets = {
            'first_name':forms.TextInput(attrs={"class":"form-control", "placeholder":'First Name', 'id':'first_name', 'required': 'True'}),
            'middle_name':forms.TextInput(attrs={"class":"form-control", "placeholder":'Middle Name','id':'middle_name'}),
            'last_name':forms.TextInput(attrs={"class":"form-control", "placeholder":'Last Name', 'id':'last_name', 'required': 'True'}),
            'mobile_number':forms.TextInput(attrs={"class":"form-control", "placeholder":'Mobile Number', 'id':'mobile_number'}),
        }
       

class ProfileForm(forms.ModelForm):
    gender_choices = (
        ('','-------'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    gender = forms.ChoiceField(choices=gender_choices, widget=forms.Select(attrs={"class":"form-select", "placeholder":"Select Gender", 'required': 'True'}))
    class Meta:
        model = Profile
        fields = ['gender', 'bio', 'street_adress', 'birth_date', 'current_city', 'home_town', 'religious_view', 'political_view', 'birth_place', 'language']

        widgets = {
            # 'gender': forms.Select(),
            'bio':forms.Textarea(attrs={"class":"form-control", "placeholder":"Bio...", 'rows': 6, 'id':'bio' }),
            'street_adress':forms.TextInput(attrs={"class":"form-control", "placeholder":'Street Adress', 'id':'street_adress'}),
            'birth_date':forms.TextInput(attrs={"class":"form-control", "placeholder":'DOB', 'type':'date', 'id':'birth_date'}),
            'current_city':forms.TextInput(attrs={"class":"form-control", "placeholder":"Current City", 'id':'current_city'}),
            'home_town':forms.TextInput(attrs={"class":"form-control", "placeholder":"Home Town",'id':'home_town' }),
            'religious_view':forms.Textarea(attrs={"class":"form-control", "placeholder":"Religious View...", 'rows': 6, 'id': 'religious_view'}),
            'political_view':forms.Textarea(attrs={"class":"form-control", "placeholder":"Political View...", 'rows': 6, 'id': 'political_view'}),
            'birth_place':forms.TextInput(attrs={"class":"form-control", "placeholder":"Birth place", 'id':'birth_place'}),
            'language':forms.TextInput(attrs={"class":"form-control", "placeholder":'Language', 'id':'language'}),
        }


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255,required=True, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'enter username', 'required':'true', 'autocomplete':'off'}))
    password = forms.CharField(required=True,  widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'***********', 'required':'true', 'autocomplete':'off', 'aria-describedby':'password-addon'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_admin:
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user