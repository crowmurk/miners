from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

from .models import Miner, Request, Server
from .forms import (
    MinerForm,
    RequestForm,
    ServerForm
)

# Create your views here.

class MinerList(ListView):
    model = Miner


class MinerCreate(CreateView):
    model = Miner
    form_class = MinerForm


class MinerUpdate(UpdateView):
    model = Miner
    form_class = MinerForm


class MinerDelete(DeleteView):
    model = Miner
    success_url = reverse_lazy('miner:miner:list')


class RequestList(ListView):
    model = Request


class RequestCreate(CreateView):
    model = Request
    form_class = RequestForm


class RequestUpdate(UpdateView):
    model = Request
    form_class = RequestForm


class RequestDelete(DeleteView):
    model = Request
    success_url = reverse_lazy('miner:request:list')


class ServerList(ListView):
    model = Server


class ServerCreate(CreateView):
    model = Server
    form_class = ServerForm


class ServerUpdate(UpdateView):
    model = Server
    form_class = ServerForm


class ServerDelete(DeleteView):
    model = Server
    success_url = reverse_lazy('miner:server:list')
