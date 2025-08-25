from django import forms
from .models import Product


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        price = cleaned.get("price")
        stock = cleaned.get("stock")
        if price is not None and price <= 0:
            self.add_error("price", "Price must be > 0")
        if stock is not None and stock < 0:
            self.add_error("stock", "Stock cannot be negative")
        return cleaned
