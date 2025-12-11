from django import forms
from .models import Expense


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["date", "amount", "category", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "border rounded p-2 w-full"}),
            "amount": forms.NumberInput(attrs={"class": "border rounded p-2 w-full", "step": "0.01", "placeholder": "0.00"}),
            "category": forms.TextInput(attrs={"class": "border rounded p-2 w-full", "placeholder": "e.g., Food, Transport"}),
            "description": forms.TextInput(attrs={"class": "border rounded p-2 w-full", "placeholder": "Optional notes"}),
        }
