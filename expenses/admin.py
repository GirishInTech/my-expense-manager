from django.contrib import admin
from .models import Expense, ViewPassword


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "amount", "category")
    search_fields = ("category", "description")
    list_filter = ("date", "category")


@admin.register(ViewPassword)
class ViewPasswordAdmin(admin.ModelAdmin):
    list_display = ("label", "password", "is_active", "created_at")
    search_fields = ("label", "password")
    list_filter = ("is_active", "created_at")
