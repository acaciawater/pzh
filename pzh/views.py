'''
Created on Feb 21, 2015

@author: theo
'''
from acacia.meetnet.views import NetworkView
from acacia.meetnet.models import Network
 
class HomeView(NetworkView):
    template_name = 'pzh/network_detail.html'

    def get_context_data(self, **kwargs):
        context = NetworkView.get_context_data(self, **kwargs)
        context['maptype'] = 'ROADMAP'
        return context

    def get_object(self):
        return Network.objects.first()
