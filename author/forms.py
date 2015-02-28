from django import forms

from .models import Authors

class NewForm(forms.ModelForm):
    name = forms.CharField(required=True)
    username = forms.CharField(required=True)
    image = forms.ImageField(required=False)
    email = forms.EmailField(required=True)
    location = forms.CharField(required=False)
    github = forms.CharField(required=False)
    twitter = forms.CharField(required=False)
    facebook = forms.CharField(required=False)
    
    class Meta:
        model = Authors


#def cleaned_image(self):
#       image = self.cleaned_data.get['image']
#       if image:
    # do some validation, if it fails
    #           raise forms.ValidationError(u'Form error')
#   return image
# fields = ('name')