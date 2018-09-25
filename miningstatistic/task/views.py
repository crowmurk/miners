from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView
)

from .models import Config
from .forms import ConfigForm

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
