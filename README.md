# Український Форум

Платформа для обговорення та обміну думками, розроблена на Django.

## Особливості

- Система користувачів з ролями (суперадміністратор, адміністратор, студент)
- Керування постами, коментарями та розділами
- Система тегів для організації контенту
- Голосування за пости та коментарі
- Сповіщення електронною поштою
- Адміністративна панель для керування контентом

## Технічні вимоги

- Python 3.10+
- Django 5.2
- Інші залежності вказані в requirements.txt

## Інструкції з розгортання на PythonAnywhere

### 1. Створіть обліковий запис на PythonAnywhere

Зареєструйтесь на [PythonAnywhere](https://www.pythonanywhere.com/) (безкоштовний тариф підійде для початку).

### 2. Налаштуйте базу даних

PythonAnywhere надає MySQL бази даних. Створіть нову базу даних через панель керування PythonAnywhere:

1. Перейдіть до вкладки "Databases"
2. Створіть нову MySQL базу даних
3. Запам'ятайте ім'я бази даних, ім'я користувача та пароль

### 3. Завантажте код на PythonAnywhere

Використовуйте Bash консоль PythonAnywhere для клонування репозиторію:

```bash
# Перейдіть до домашньої директорії
cd ~

# Клонуйте репозиторій (замініть URL на ваш)
git clone https://github.com/yourusername/forum.git

# Перейдіть до директорії проекту
cd forum
```

### 4. Налаштуйте віртуальне середовище

```bash
# Створіть віртуальне середовище
python -m venv venv

# Активуйте віртуальне середовище
source venv/bin/activate

# Встановіть залежності
pip install -r requirements.txt
```

### 5. Налаштуйте файл налаштувань

Відредагуйте файл `forum/wsgi_pythonanywhere.py` та змініть:

1. Шлях до вашого проекту (`path = '/home/yourusername/forum'`)
2. Секретний ключ (`os.environ['DJANGO_SECRET_KEY'] = 'your-secret-key-here'`)

### 6. Налаштуйте веб-додаток на PythonAnywhere

1. Перейдіть до вкладки "Web" на PythonAnywhere
2. Натисніть "Add a new web app"
3. Виберіть "Manual configuration" (не "Django")
4. Виберіть версію Python 3.10

### 7. Налаштуйте WSGI файл

На сторінці налаштувань веб-додатка знайдіть розділ "Code" і натисніть на посилання WSGI файлу.
Замініть вміст цього файлу на вміст вашого `forum/wsgi_pythonanywhere.py`.

### 8. Налаштуйте шляхи до статичних файлів

На сторінці налаштувань веб-додатка знайдіть розділ "Static files" і додайте:

1. URL: `/static/` → Directory: `/home/yourusername/forum/staticfiles`
2. URL: `/media/` → Directory: `/home/yourusername/forum/media`

### 9. Застосуйте міграції та зберіть статичні файли

У Bash консолі PythonAnywhere виконайте:

```bash
# Активуйте віртуальне середовище
cd ~/forum
source venv/bin/activate

# Застосуйте міграції
python manage.py migrate

# Зберіть статичні файли
python manage.py collectstatic --noinput

# Створіть суперкористувача
python manage.py createsuperuser
```

### 10. Перезавантажте веб-додаток

Натисніть кнопку "Reload" на сторінці налаштувань веб-додатка.

Ваш форум тепер повинен бути доступний за адресою `yourusername.pythonanywhere.com`.

## Налаштування електронної пошти

Для налаштування відправки електронної пошти через Gmail:

1. Створіть пароль додатка в налаштуваннях безпеки вашого облікового запису Google
2. Додайте наступні змінні середовища в файл `forum/wsgi_pythonanywhere.py`:

```python
os.environ['EMAIL_HOST_USER'] = 'your-email@gmail.com'
os.environ['EMAIL_HOST_PASSWORD'] = 'your-app-password'
```

## Ліцензія

MIT
