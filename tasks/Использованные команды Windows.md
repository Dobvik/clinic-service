# Использованные команды для Windows


Команды предназначены для PowerShell (в том числе в Windows Terminal). Git и Python 3 должны быть установлены. Команды запуска и проверок выполняются из корня проекта.

Активация виртуального окружения не требуется: команды напрямую вызывают Python из `.venv`.

## Навигация в терминале

```powershell
Get-Location
Get-ChildItem
cd "C:\projects\clinic-service"
```

В команде `cd` замените путь на папку своего проекта.


## Запуск приложения 

### Запуск

Первый раз при открытии проекта:  
```
py -3 -m venv .venv
```
```
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```  

Запуск:

```powershell
.\.venv\Scripts\python.exe -m app --demo --port 8000
```

Остановить приложение: `Ctrl+C`.


### Проверки

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
```


## Git
```
git --version
```

### Конфигурация
```
git config --global user.name "Ivan Ivanov"
git config --global user.email "ivan@example.com"
```

### Работа с репозиторием

Склонировать репозиторий
```
git clone URL
cd clinic-service
```

В `git clone` замените `URL` на адрес репозитория, а в `cd` — `clinic-service` на имя созданной папки.

Измененные файлы и их статус
```
git status
```

Создать ветку  
```
git checkout -b feature/search
```

Переключиться на ветку
```
git checkout main
```

Добавить все файлы в индекс
```
git add .
```

Сделать коммит
```
git commit -m "сообщение"
```


### Сценарий "сохранение изменений"
```
# Проверить, что изменилось
git status
git diff

# Подготовить конкретный файл к коммиту
git add app/main.py

# Или подготовить все изменения из текущей папки и подпапок
git add .

# Проверить содержимое будущего коммита
git diff --staged

# Создать коммит
git commit -m "Добавлен поиск врачей"
```

### Сценарий "сделать новую фичу и открыть pull request"

```
# Перейти в основную ветку и обновить её
git checkout main
git pull --ff-only

# Создать ветку для задачи
git checkout -b feature/search

# Внести изменения в код...

# Проверить и сохранить изменения
git status
git diff
git add .
git diff --staged
git commit -m "Добавлен поиск врачей"

# Отправить ветку на GitHub
git push -u origin feature/search
```

После отправки ветки откройте репозиторий на GitHub и создайте pull request из `feature/search` в `main`.
