from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Income, Expense, Limit
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

import matplotlib.pyplot as plt
import io
import urllib, base64
from django.shortcuts import render
from .models import Income, Expense


def home(request):
    if request.method == 'POST':
        return redirect('login')
    return render(request, 'finance/home.html')


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Проверка на пустые поля
        if not username or not password:
            return render(request, 'finance/login.html', {'error': 'Username and password are required'})

        # Аутентификация пользователя
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('income')
        else:
            return render(request, 'finance/login.html', {'error': 'Invalid credentials'})

    return render(request, 'finance/login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Проверка на пустые поля
        if not username or not password:
            return render(request, 'finance/register.html', {'error': 'Username and password are required'})

        # Проверка на существование пользователя с таким же именем
        if User.objects.filter(username=username).exists():
            return render(request, 'finance/register.html', {'error': 'Username already exists'})

        # Создание нового пользователя
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('login')

    return render(request, 'finance/register.html')

from django.shortcuts import render, redirect
from .models import Income, Expense, Limit
import matplotlib.pyplot as plt
import io
import base64

from decimal import Decimal, InvalidOperation

def income_view(request):
    if request.method == 'POST':
        # Получение данных из формы
        income_amount = request.POST.get('Доход')
        expenses = {
            'Еда': request.POST.get('Еда', 0),
            'Транспорт': request.POST.get('Транспорт', 0),
            'Связь': request.POST.get('Связь', 0),
            'Медицина': request.POST.get('Медицина', 0),
            'Красота': request.POST.get('Красота', 0),
            'Маркетплейсы': request.POST.get('Маркетплейсы', 0),
            'Развлечения': request.POST.get('Развлечения', 0),
            'Кредит': request.POST.get('Кредит', 0),
            'Учеба': request.POST.get('Учеба', 0),
            'Одежда и обувь': request.POST.get('Одежда и обувь', 0),
        }

        # Получение лимита на траты
        limit_amount = request.POST.get('limit_amount', 0)  # Изменено на 'limit_amount'
        if limit_amount:
            try:
                limit_amount = Decimal(limit_amount)
                # Сохранение лимита в базе данных
                Limit.objects.update_or_create(user=request.user, defaults={'amount': limit_amount})
            except InvalidOperation:
                return render(request, 'finance/income.html', {'error': 'Введите корректную сумму лимита'})

        # Проверка на пустое значение и конвертация в Decimal
        if income_amount:
            try:
                income_amount = Decimal(income_amount)
                Income.objects.create(user=request.user, amount=income_amount)
            except InvalidOperation:
                return render(request, 'finance/income.html', {'error': 'Введите корректную сумму дохода'})

        total_expense = Decimal('0')
        # Сохранение расходов
        for category, amount in expenses.items():
            if amount:  # Сохраняем только если сумма больше 0
                try:
                    amount = Decimal(amount)  # Преобразование в Decimal
                    total_expense += amount
                    Expense.objects.create(user=request.user, amount=amount, category=category)
                except InvalidOperation:
                    return render(request, 'finance/income.html', {'error': f'Введите корректную сумму для {category}'})

        # Проверка на превышение лимита
        limit = Limit.objects.filter(user=request.user).first()
        limit_amount = limit.amount if limit else Decimal('inf')
        if total_expense > limit_amount:
            return render(request, 'finance/income.html', {'error': 'Сумма расходов превышает лимит на траты'})

        return redirect('generate_chart')  # Перенаправление на генерацию диаграммы

    Income.objects.filter(user=request.user).delete()
    Expense.objects.filter(user=request.user).delete()
    return render(request, 'finance/income.html')

import matplotlib
matplotlib.use('Agg')  # Используем бэкенд Agg
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from .models import Income, Expense

def generate_chart(request):
    if request.user.is_authenticated:
        incomes = Income.objects.filter(user=request.user)
        expenses = Expense.objects.filter(user=request.user)

        income_data = [income.amount for income in incomes]
        expense_data = {expense.category: expense.amount for expense in expenses}

        # Создание диаграммы
        plt.figure(figsize=(16, 6))
        plt.bar(['Доходы'] + list(expense_data.keys()), [sum(income_data)] + list(expense_data.values()), color=['green'] + ['red'] * len(expense_data))
        plt.title('Доходы vs Расходы')
        plt.ylabel('Рубли')

        # Установка цвета фона диаграммы
        plt.gcf().patch.set_facecolor('#E0EEF3')  # Установка цвета фона диаграммы

        # Сохранение диаграммы в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_png = buf.getvalue()
        buf.close()
        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')

        return render(request, 'finance/chart.html', {'graphic': graphic, 'expense_data': expense_data})
    return redirect('login')
