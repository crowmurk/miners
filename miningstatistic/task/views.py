from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView
)

from .models import Config, ServerTask
from .forms import ConfigForm, ServerTaskForm

# Create your views here.

class ListViewMixin():
    def get_context_data(self):
        context = super(ListView, self).get_context_data()
        context['model'] = self.model
        return context


class ConfigList(ListViewMixin, ListView):
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


class ServerTaskList(ListViewMixin, ListView):
    model = ServerTask
    paginate_by = 7


class ServerTaskCreate(CreateView):
    model = ServerTask
    form_class = ServerTaskForm


class ServerTaskDetail(DetailView):
    model = ServerTask
    form_class = ServerTaskForm


class ServerTaskUpdate(UpdateView):
    model = ServerTask
    form_class = ServerTaskForm


class ServerTaskDelete(DeleteView):
    model = ServerTask
    success_url = reverse_lazy('task:server:list')
