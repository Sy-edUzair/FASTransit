from django import forms

class VoucherUploadForm(forms.Form): 
    file = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(
            attrs={
                'id': 'voucher-file',
                'name': 'voucher_image',  
                'accept': 'image/png, image/jpeg',  
            }
        )
    )