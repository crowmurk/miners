from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView
)

from django_tables2 import SingleTableView

from .models import Config, ServerTask, ServerStatistic
from .forms import ConfigForm, ServerTaskForm
from .tables import ServerStatisticTable

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


class ServerTaskList(ListView):
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
    success_url = reverse_lazy('task:servertask:list')


class ServerStatisticList(SingleTableView):
    table_class = ServerStatisticTable
    queryset = ServerStatistic.objects.results_last()
