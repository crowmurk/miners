from logging import Filter


class ManagementFilter(Filter):
    def filter(self, record):
        """Фильтрует вывод запросов БД из лога
        """
        if hasattr(record, 'funcName') and record.funcName == 'execute':
            return False
        return True
