from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
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

class ConfigList(ListView):
    model = Config
    paginate_by = 7


class ConfigCreate(LoginRequiredMixin, CreateView):
    model = Config
    form_class = ConfigForm


class ConfigDetail(DetailView):
    model = Config
    form_class = ConfigForm


class ConfigUpdate(LoginRequiredMixin, UpdateView):
    model = Config
    form_class = ConfigForm


class ConfigDelete(LoginRequiredMixin, DeleteView):
    model = Config
    success_url = reverse_lazy('task:config:list')


class ServerTaskList(ListView):
    model = ServerTask
    paginate_by = 7


class ServerTaskCreate(LoginRequiredMixin, CreateView):
    model = ServerTask
    form_class = ServerTaskForm


class ServerTaskDetail(DetailView):
    model = ServerTask
    form_class = ServerTaskForm


class ServerTaskUpdate(LoginRequiredMixin, UpdateView):
    model = ServerTask
    form_class = ServerTaskForm


class ServerTaskDelete(LoginRequiredMixin, DeleteView):
    model = ServerTask
    success_url = reverse_lazy('task:server:list')
