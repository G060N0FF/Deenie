from django import forms

class PlaylistForm(forms.Form):
    text = forms.CharField(widget=forms.TextInput(attrs={'class':'plform'}) ,max_length=200, label="")

class SearchForm(forms.Form):
    keyword=forms.CharField(widget=forms.TextInput(attrs={'class':'search', 'placeholder':'Search'}), max_length=200, label="")