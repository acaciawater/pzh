'''
Created on Feb 21, 2015

@author: theo
'''
from acacia.meetnet.views import NetworkView
from acacia.meetnet.models import Network, Well
from django.views.generic.detail import DetailView
 
class HomeView(NetworkView):
    template_name = 'pzh/network_detail.html'

    def get_context_data(self, **kwargs):
        context = NetworkView.get_context_data(self, **kwargs)
        context['maptype'] = 'ROADMAP'
        return context

    def get_object(self):
        return Network.objects.first()

class NavMixin(object):

    def nav(self,obj):
        next = obj.__class__.objects.filter(pk__gt=obj.pk)
        next = next.first() if next else None
        prev = obj.__class__.objects.filter(pk__lt=obj.pk)
        prev = prev.last() if prev else None
        return {'next': next, 'prev': prev}
    
class MaintenanceView(NavMixin, DetailView):
    model=Well
    template_name = 'pzh/maintenance.html'
    
    def get_context_data(self, **kwargs): 
        context = super(MaintenanceView, self).get_context_data(**kwargs)
        obj = self.get_object()
        context['nav'] = self.nav(obj)
        return context               
