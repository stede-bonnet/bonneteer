from django import forms

class SearchForm(forms.Form):
    search = forms.CharField(label="searchWord",max_length=100,widget=forms.TextInput(attrs={'placeholder':'Enter game'}))

