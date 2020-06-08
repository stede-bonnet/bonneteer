from django import forms

class SearchForm(forms.Form):
    search = forms.CharField(label="searchWord",max_length=100,widget=forms.TextInput(attrs={'placeholder':'What game can Bonneteer help you with today?'}))

