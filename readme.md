# Запуск тестового сервера

Создаем виртуальное окружение Python:

```bash
python -m venv test
cd test
```

Активируем виртуальное окружение:

```bash
source bin/activate
```

Клонируем репозиторий:

```bash
git clone https://github.com/crowmurk/miners
cd miners
```

Переключаемся на ветку develop-django:

```bash
git checkout develop-django
```

Обновляем pip:

```bash
pip install --upgrade pip
```

Устанавливаем зависимости: Для установки модуля `pygraphviz==1.5` из `requrements.txt` может потребоваться пакет `graphviz` (так он называется в arch) Версия: 2.40.1-13 [graphviz.org](http://www.graphviz.org/). Для нормальной работы он не нужен (см. ниже), если возникнут проблемы, его можно удалить из `requrements.txt`

```bash
pip install -r requirements.txt
pip install ./pyminers
pip install ./pypools
```

Создаем БД django:

```bash
cd miningstatistic
./manage.py migrate
```

Опрашиваем майнеры, высыпятся предупреждения, это нормально, майнеры не доступны:

```bash
python ../dj-miners.py
```

Запускаем тестовый сервер django (прервать работу сервера: `Ctrl-C`):

```bash
./manage.py runserver
```

Заходим в браузере: [localhost:8000](http://localhost:8000)

Для графичиского представления моделей БД (для чего и нужен `graphviz`) выполнить:

```bash
./manage.py graph_models miner task statistic --pygraphviz -g -o db_visualized.png
```

Деактивируем виртуальное окружение Python:

```bash
deactivate
```
