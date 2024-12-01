from django import forms

class GenerateVoucherForm(forms.ModelForm):
    semester = forms.CharField(max_length=100, required=True, label='Semester')
    