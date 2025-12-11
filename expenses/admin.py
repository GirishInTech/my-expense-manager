from django.contrib import admin
from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "amount", "category")
    search_fields = ("category", "description")
    list_filter = ("date", "category")
