from django import forms
from .models import ProgramRegister

class ProgramRegisterForm(forms.ModelForm):
    class Meta:
        model = ProgramRegister
        fields = [
            "name",
            "age",
            "email",
            "phone",
            "gender",
            "college",
            "department",
            "year",
            "linkedin",
            "github",
            "portfolio",
            "twitter",
        ]
 