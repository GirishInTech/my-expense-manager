from datetime import date
from calendar import monthrange
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

from .models import Expense
from .forms import ExpenseForm


def _get_month_range(year: int, month: int):
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    return first_day, last_day


def dashboard(request):
    today = timezone.localdate()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))
    
    # Get date filter parameters
    filter_start = request.GET.get("filter_start")
    filter_end = request.GET.get("filter_end")

    if request.method == "POST" and request.user.is_staff:
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense added successfully!")
            return redirect("dashboard")
    else:
        form = ExpenseForm(initial={"date": today}) if request.user.is_staff else None

    start, end = _get_month_range(year, month)
    
    # Apply date filters if provided
    if filter_start and filter_end:
        try:
            from datetime import datetime
            start = datetime.strptime(filter_start, "%Y-%m-%d").date()
            end = datetime.strptime(filter_end, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
    
    qs = Expense.objects.filter(date__range=(start, end)).order_by("-date", "-id")

    total_for_month = qs.aggregate(total=Sum("amount"))["total"] or 0

    # Daily totals
    daily_totals_qs = (
        Expense.objects.filter(date__range=(start, end))
        .values("date")
        .annotate(total=Sum("amount"))
        .order_by("date")
    )
    daily_breakdown = list(daily_totals_qs)

    # Show all expenses for the month instead of limiting to 10
    all_expenses = list(qs)

    context = {
        "year": year,
        "month": month,
        "total_for_month": total_for_month,
        "daily_breakdown": daily_breakdown,
        "expenses": all_expenses,
        "months": range(1, 13),
        "form": form,
        "filter_start": filter_start or start,
        "filter_end": filter_end or end,
    }
    return render(request, "dashboard.html", context)


def monthly_view(request, year: int, month: int):
    start, end = _get_month_range(year, month)
    qs = Expense.objects.filter(date__range=(start, end)).order_by("date", "id")
    total_for_month = qs.aggregate(total=Sum("amount"))["total"] or 0
    context = {
        "year": year,
        "month": month,
        "total_for_month": total_for_month,
        "expenses": qs,
    }
    return render(request, "monthly.html", context)


def api_expenses(request):
    data = list(
        Expense.objects.all()
        .order_by("-date", "-id")
        .values("id", "date", "amount", "category", "description")
    )
    return JsonResponse(data, safe=False)


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("dashboard")


def edit_expense(request, expense_id):
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to edit expenses.")
        return redirect("dashboard")
    
    expense = get_object_or_404(Expense, id=expense_id)
    
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully!")
            return redirect("dashboard")
    else:
        form = ExpenseForm(instance=expense)
    
    context = {
        "form": form,
        "expense": expense,
        "is_edit": True,
    }
    return render(request, "edit_expense.html", context)


def delete_expense(request, expense_id):
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to delete expenses.")
        return redirect("dashboard")
    
    expense = get_object_or_404(Expense, id=expense_id)
    
    if request.method == "POST":
        expense.delete()
        messages.success(request, "Expense deleted successfully!")
        return redirect("dashboard")
    
    context = {"expense": expense}
    return render(request, "delete_expense.html", context)
