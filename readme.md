<<<<<<< HEAD
- [Запуск тестового сервера](#запуск-тестового-сервера)
- [Run a test server](#run-a-test-server)
=======
[Запуск тестового сервера](#запуск-тестового-сервера)
[Run a test server](#run-a-test-server)
>>>>>>> f8bb1dc28924a6f3987136a1f41df7cc2fda8c94

# Run a test server

Create a Python virtual environment:

```bash
python -m venv test
cd test
```

Enable the virtual environment:

```bash
source bin/activate
```

Clone the repository:

```bash
git clone https://github.com/crowmurk/miners
cd miners
```

Switch to the `develop-django` branch:

```bash
git checkout develop-django
```

Upgrade `pip`:

```bash
pip install --upgrade pip
```

Install dependencies:  to install `pygraphviz==1.5` package [graphviz 2.40.1-13](https://www.archlinux.org/packages/extra/x86_64/graphviz/) may be required (more about at [graphviz.org](http://www.graphviz.org/)). Normally `pygraphviz` package is not required (see below). If there are any problems, then the package can be removed from `requrements.txt`

```bash
pip install -r requirements.txt
pip install ./pyminers
pip install ./pypools
```

Create a django database :

```bash
cd miningstatistic
./manage.py migrate
```

Request miners. Warning messages will appear. Disregard them. Miners are not available:

```bash
python ../dj-miners.py
```

Run a django test server (to stop the server press `Ctrl-C`):

```bash
./manage.py runserver
```

Open in web browser: [localhost:8000](http://localhost:8000)

Execute the command for graphical representation of database models (this is the reason we use `graphviz`)

```bash
./manage.py graph_models miner task statistic --pygraphviz -g -o db_visualized.png
```

Deacivate the Python virtual environment:

```bash
deactivate
```

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

Переключаемся на ветку `develop-django`:

```bash
git checkout develop-django
```

Обновляем `pip`:

```bash
pip install --upgrade pip
```

Устанавливаем зависимости: Для установки модуля `pygraphviz==1.5` может потребоваться [graphviz 2.40.1-13](https://www.archlinux.org/packages/extra/x86_64/graphviz/) (подробней на [graphviz.org](http://www.graphviz.org/)). Для нормальной работы он не нужен (см. ниже), если возникнут проблемы, его можно удалить из `requrements.txt`

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

Опрашиваем майнеры, появятся предупреждения, это нормально, майнеры не доступны:

```bash
python ../dj-miners.py
```

Запускаем тестовый сервер django (прервать работу сервера: `Ctrl-C`):

```bash
./manage.py runserver
```

Заходим в браузере: [localhost:8000](http://localhost:8000)

Для графического представления моделей БД (для чего и нужен `graphviz`) выполнить:

```bash
./manage.py graph_models miner task statistic --pygraphviz -g -o db_visualized.png
```

Деактивируем виртуальное окружение Python:

```bash
deactivate
```
