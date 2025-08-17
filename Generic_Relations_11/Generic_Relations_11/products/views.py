from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Product, Category, Supplier
from comments.models import Comment
from ratings.models import Rating


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch generic comments and ratings for this product
        context['comments'] = Comment.objects.filter(
            content_type__model='product', object_id=self.object.pk
        ).order_by('-created_at')
        context['ratings'] = Rating.objects.filter(
            content_type__model='product', object_id=self.object.pk
        ).order_by('-created_at')
        return context
