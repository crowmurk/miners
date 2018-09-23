from django.shortcuts import get_object_or_404

from .models import Miner, Request


class MinerContextMixin():
    # Имя переданного аргумента в URLConf,
    # содержащего значение slug
    miner_slug_url_kwarg = 'miner_slug'
    # Имя переменной для использования в контексте
    miner_context_object_name = 'miner'

    def get_context_data(self, **kwargs):
        """Добавляет объект Miner в контекст представлений Request
        """
        if hasattr(self, 'miner'):
            context = {
                # Добавляем в контекст имеющися объект
                self.miner_context_object_name: self.miner,
            }
        else:
            # Извлекаем переданный slug
            miner_slug = self.kwargs.get(self.miner_slug_url_kwarg)
            # Получаем объект
            miner = get_object_or_404(
                Miner,
                slug__iexact=miner_slug,
            )
            # Добавляем в контекст
            context = {self.miner_context_object_name: miner, }
        context.update(kwargs)
        return super().get_context_data(**context)


class RequestGetObjectMixin():
    def get_object(self, queryset=None):
        """Возвращает объект Request, который отображается
        представлениями
        """
        # Получаем slug из аргументов переданных представлению
        miner_slug = self.kwargs.get(self.miner_slug_url_kwarg)
        request_slug = self.kwargs.get(self.slug_url_kwarg)

        if miner_slug is None or request_slug is None:
            raise AttributeError(
                "Generic detail view %s must be called with "
                "either a miner_slug  and a request_slug."
                % self.__class__.__name__
            )
        return get_object_or_404(
            Request,
            slug__iexact=request_slug,
            miner__slug__iexact=miner_slug,
        )
