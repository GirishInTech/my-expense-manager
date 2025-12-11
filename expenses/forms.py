from django import forms
from .models import Expense


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["date", "amount", "category", "description"]
        widgets = {
            "date": forms.DateInput(attrs={
                "type": "date", 
                "class": "border rounded p-2 w-full text-base",
                "style": "min-height: 44px;",
            }),
            "amount": forms.NumberInput(attrs={
                "class": "border rounded p-2 w-full text-base", 
                "step": "0.01", 
                "placeholder": "0.00",
                "style": "min-height: 44px;",
                "inputmode": "decimal",
            }),
            "category": forms.TextInput(attrs={
                "class": "border rounded p-2 w-full text-base", 
                "placeholder": "e.g., Food, Transport",
                "style": "min-height: 44px;",
                "list": "category-suggestions",
            }),
            "description": forms.TextInput(attrs={
                "class": "border rounded p-2 w-full text-base", 
                "placeholder": "Optional notes",
                "style": "min-height: 44px;",
            }),
        }
