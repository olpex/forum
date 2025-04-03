# Розгортання Українського Форуму на Vercel

Це керівництво допоможе вам розгорнути Django-форум на платформі Vercel.

## Передумови

1. Обліковий запис [Vercel](https://vercel.com/)
2. Обліковий запис [GitHub](https://github.com/) (для зберігання коду)
3. База даних PostgreSQL (можна використовувати [Supabase](https://supabase.com/) або [Neon](https://neon.tech/) для безкоштовної PostgreSQL бази даних)

## Крок 1: Підготуйте свій проект для GitHub

```bash
# Ініціалізуйте Git репозиторій (якщо ще не зроблено)
git init
git add .
git commit -m "Підготовка до розгортання на Vercel"

# Створіть репозиторій на GitHub і завантажте код
git remote add origin https://github.com/your-username/forum.git
git push -u origin main
```

## Крок 2: Налаштуйте базу даних PostgreSQL

1. Створіть безкоштовну базу даних на [Supabase](https://supabase.com/) або [Neon](https://neon.tech/)
2. Запишіть дані для підключення:
   - Ім'я бази даних
   - Ім'я користувача
   - Пароль
   - Хост
   - Порт

## Крок 3: Розгорніть на Vercel

1. Увійдіть до [Vercel](https://vercel.com/)
2. Натисніть "Add New..." > "Project"
3. Імпортуйте свій GitHub репозиторій
4. Налаштуйте змінні середовища:

   | Змінна | Значення |
   |--------|----------|
   | DJANGO_SECRET_KEY | Ваш секретний ключ |
   | DJANGO_DEBUG | False |
   | POSTGRES_NAME | Ім'я бази даних |
   | POSTGRES_USER | Ім'я користувача |
   | POSTGRES_PASSWORD | Пароль |
   | POSTGRES_HOST | Хост бази даних |
   | POSTGRES_PORT | Порт бази даних (зазвичай 5432) |
   | EMAIL_HOST_USER | Ваша Gmail адреса (опціонально) |
   | EMAIL_HOST_PASSWORD | Пароль додатка Gmail (опціонально) |

5. Натисніть "Deploy"

## Крок 4: Створіть суперкористувача

Після розгортання вам потрібно створити суперкористувача. Оскільки Vercel не надає прямого доступу до командного рядка, вам потрібно:

1. Додати тимчасовий URL-шлях для створення суперкористувача
2. Видалити цей шлях після створення

Додайте наступний код до `users/views.py`:

```python
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def create_superuser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not username or not email or not password:
            return HttpResponse('Всі поля обов\'язкові', status=400)
        
        User = get_user_model()
        
        if User.objects.filter(username=username).exists():
            return HttpResponse('Користувач вже існує', status=400)
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        return HttpResponse(f'Суперкористувач {username} створено успішно!')
    
    return HttpResponse('''
    <form method="post">
        <h1>Створення суперкористувача</h1>
        <div>
            <label>Ім'я користувача:</label>
            <input type="text" name="username" required>
        </div>
        <div>
            <label>Email:</label>
            <input type="email" name="email" required>
        </div>
        <div>
            <label>Пароль:</label>
            <input type="password" name="password" required>
        </div>
        <button type="submit">Створити</button>
    </form>
    ''')
```

Додайте URL-шлях до `users/urls.py`:

```python
path('create-superuser/', views.create_superuser, name='create_superuser'),
```

Після створення суперкористувача **обов'язково видаліть** цей код з міркувань безпеки!

## Крок 5: Налаштування статичних файлів

Vercel автоматично обслуговує статичні файли з директорії `staticfiles`. Переконайтеся, що ви виконали команду `python manage.py collectstatic` перед розгортанням або використовуйте наш скрипт `build_files.sh`.

## Обмеження Vercel для Django

1. **Serverless функції**: Vercel використовує serverless архітектуру, що може спричинити "холодний старт" вашого додатка.
2. **Файлова система**: Vercel має тільки тимчасову файлову систему. Для завантаження файлів використовуйте зовнішнє сховище, як-от AWS S3.
3. **Тривалі з'єднання**: Vercel не підтримує WebSockets або тривалі з'єднання.

## Альтернативи

Якщо Vercel не відповідає вашим потребам, розгляньте:

1. **PythonAnywhere**: Спеціалізований хостинг для Python додатків
2. **Heroku**: Платформа, що добре підтримує Django
3. **Railway**: Проста платформа з підтримкою PostgreSQL
4. **DigitalOcean App Platform**: Повнофункціональний хостинг з контейнерами

## Усунення несправностей

1. **500 помилки**: Перевірте журнали розгортання на Vercel
2. **Проблеми з базою даних**: Переконайтеся, що IP вашого Vercel додатка дозволений у налаштуваннях бази даних
3. **Статичні файли не завантажуються**: Перевірте, чи правильно налаштовано `STATIC_ROOT` та `STATICFILES_DIRS`
