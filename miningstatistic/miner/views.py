from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView
)

from .models import Miner, Request, Server
from .forms import (
    MinerForm,
    RequestForm,
    ServerForm
)
from .utils import (
    RequestGetObjectMixin,
    MinerContextMixin,
)

# Create your views here.

class MinerList(ListView):
    model = Miner
    paginate_by = 7


class MinerCreate(CreateView):
    model = Miner
    form_class = MinerForm


class MinerDetail(DetailView):
    model = Miner
    form_class = MinerForm


class MinerUpdate(UpdateView):
    model = Miner
    form_class = MinerForm


class MinerDelete(DeleteView):
    model = Miner
    success_url = reverse_lazy('miner:miner:list')


class RequestCreate(
        RequestGetObjectMixin,
        MinerContextMixin,
        CreateView,
):
    model = Request
    form_class = RequestForm

    def get_initial(self):
        # Добавляем к начальным данным представления
        # ассоциированный майнер
        miner_slug = self.kwargs.get(self.miner_slug_url_kwarg)
        self.miner = get_object_or_404(Miner, slug__iexact=miner_slug)
        initial = {self.miner_context_object_name: self.miner, }
        initial.update(self.initial)
        return initial


class RequestDetail(
        RequestGetObjectMixin,
        MinerContextMixin,
        DetailView,
):
    model = Request
    form_class = RequestForm
    # Имя аргумента с переданным slug
    slug_url_kwarg = 'request_slug'


class RequestUpdate(
        RequestGetObjectMixin,
        MinerContextMixin,
        UpdateView,
):
    model = Request
    form_class = RequestForm
    # Имя аргумента с переданным slug
    slug_url_kwarg = 'request_slug'


class RequestDelete(
        RequestGetObjectMixin,
        MinerContextMixin,
        DeleteView,
):
    model = Request
    # Имя аргумента с переданным slug
    slug_url_kwarg = 'request_slug'

    def get_success_url(self):
            return self.object.miner.get_absolute_url()


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
    success_url = reverse_lazy('miner:server:list')
