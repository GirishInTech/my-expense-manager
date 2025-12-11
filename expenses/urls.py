from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("expenses/<int:year>/<int:month>/", views.monthly_view, name="monthly"),
    path("api/expenses/", views.api_expenses, name="api_expenses"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("expense/edit/<int:expense_id>/", views.edit_expense, name="edit_expense"),
    path("expense/delete/<int:expense_id>/", views.delete_expense, name="delete_expense"),
]
