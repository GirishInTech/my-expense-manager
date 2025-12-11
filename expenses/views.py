from datetime import date
from calendar import monthrange
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings

from .models import Expense, ViewPassword
from .forms import ExpenseForm


def check_view_access(request):
    """Check if user has view access via password or admin login"""
    return request.session.get('view_access') or request.user.is_staff


def _get_month_range(year: int, month: int):
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    return first_day, last_day


def dashboard(request):
    # Check if user has view access
    if not check_view_access(request):
        return redirect('view_login')
    
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
    # Check if user has view access
    if not check_view_access(request):
        return redirect('view_login')
    
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
                request.session['view_access'] = True
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
    request.session['view_access'] = False
    messages.success(request, "You have been logged out successfully.")
    return redirect("view_login")


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


def view_login(request):
    """Login view for family members to enter view password"""
    if request.method == "POST":
        entered_password = request.POST.get("view_password")
        
        # Check against active passwords in database
        valid_password = ViewPassword.objects.filter(
            password=entered_password,
            is_active=True
        ).first()
        
        if valid_password:
            request.session['view_access'] = True
            messages.success(request, "Access granted! Welcome.")
            return redirect("dashboard")
        else:
            messages.error(request, "Incorrect password. Please try again.")
    
    return render(request, "view_login.html")


def change_view_password(request):
    """Redirect to manage_passwords"""
    return redirect('manage_passwords')


def manage_passwords(request):
    """Allow admin to manage multiple view passwords"""
    if not request.user.is_staff:
        messages.error(request, "Only admin can manage passwords.")
        return redirect("dashboard")
    
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "add":
            password = request.POST.get("password")
            label = request.POST.get("label")
            
            if password and label:
                if ViewPassword.objects.filter(password=password).exists():
                    messages.error(request, "This password already exists.")
                else:
                    ViewPassword.objects.create(password=password, label=label)
                    messages.success(request, f"Password added for '{label}': {password}")
            else:
                messages.error(request, "Both password and label are required.")
        
        elif action == "delete":
            password_id = request.POST.get("password_id")
            try:
                pwd = ViewPassword.objects.get(id=password_id)
                pwd.delete()
                messages.success(request, f"Password for '{pwd.label}' deleted.")
            except ViewPassword.DoesNotExist:
                messages.error(request, "Password not found.")
        
        elif action == "toggle":
            password_id = request.POST.get("password_id")
            try:
                pwd = ViewPassword.objects.get(id=password_id)
                pwd.is_active = not pwd.is_active
                pwd.save()
                status = "activated" if pwd.is_active else "deactivated"
                messages.success(request, f"Password for '{pwd.label}' {status}.")
            except ViewPassword.DoesNotExist:
                messages.error(request, "Password not found.")
        
        return redirect("manage_passwords")
    
    passwords = ViewPassword.objects.all()
    context = {"passwords": passwords}
    return render(request, "manage_passwords.html", context)
