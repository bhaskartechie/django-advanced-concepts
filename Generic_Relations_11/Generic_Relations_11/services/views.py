from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Service, ServiceProvider, ServiceType
from comments.models import Comment
from ratings.models import Rating


class ServiceListView(ListView):
    model = Service
    template_name = 'services/service_list.html'
    context_object_name = 'services'
    paginate_by = 10


class ServiceDetailView(DetailView):
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch generic comments and ratings for this service
        context['comments'] = Comment.objects.filter(
            content_type__model='service', object_id=self.object.pk
        ).order_by('-created_at')
        context['ratings'] = Rating.objects.filter(
            content_type__model='service', object_id=self.object.pk
        ).order_by('-created_at')
        return context
