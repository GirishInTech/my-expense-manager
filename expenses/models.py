from django.db import models


class Expense(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.date:%Y-%m-%d} - ₹{self.amount} - {self.category}"


class ViewPassword(models.Model):
    password = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=100, help_text="e.g., 'Mom', 'Dad', 'Sister'")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.label} - {self.password}"

    class Meta:
        ordering = ['-created_at']













    