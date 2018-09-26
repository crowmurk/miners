from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView
)

from .models import Config, Server
from .forms import ConfigForm, ServerForm

# Create your views here.

class ConfigList(ListView):
    model = Config
    paginate_by = 7


class ConfigCreate(CreateView):
    model = Config
    form_class = ConfigForm


class ConfigDetail(DetailView):
    model = Config
    form_class = ConfigForm


class ConfigUpdate(UpdateView):
    model = Config
    form_class = ConfigForm


class ConfigDelete(DeleteView):
    model = Config
    success_url = reverse_lazy('task:config:list')


class ServerList(ListView):
    model = Server
    paginate_by = 7


class ServerCreate(CreateView):
    model = Server
    form_class = ServerForm


class ServerDetail(DetailView):
    model = Server
    form_class = ServerForm


class ServerUpdate(UpdateView):
    model = Server
    form_class = ServerForm


class ServerDelete(DeleteView):
    model = Server
    success_url = reverse_lazy('task:server:list')
