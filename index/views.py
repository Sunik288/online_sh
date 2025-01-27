from django.shortcuts import render, redirect
from .models import Product, Category, Cart
from .forms import RegForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.views import View
import telebot


# Создаем объект бота
bot = telebot.TeleBot('7971172460:AAExavh5f0K-I6KI60IpJCB69jpoKam94v4')


# Create your views here.
# Главная страница
def home_page(request):
    # Получаем информацию из БД
    products = Product.objects.all()
    categories = Category.objects.all()
    # Отправляем данные на фронт
    context = {'products': products, 'categories': categories}

    return render(request, 'home.html', context)

# Страница выбранной категории
def category_page(request, pk):
    # Вытаскиваем выбранную категорию
    category = Category.objects.get(id=pk)
    # Фильтруем товары по выбранной категории
    products = Product.objects.filter(pr_category=category)
    # Отправляем данные на фронт
    context = {'category': category, 'products': products}

    return render(request, 'category.html', context)


# Страница выбранного продукта
def product_page(request, pk):
    # Вытаскиваем выбранный продукт
    product = Product.objects.get(id=pk)
    # Передаем данные на фронт
    context = {'product': product}

    return render(request, 'product.html', context)


# Регистрация
class Register(View):
    template_name = 'registration/register.html'

    def get(self, request):
        context = {'form': RegForm}
        return render(request, self.template_name, context)


    def post(self, request):
        form = RegForm(request.POST)

        if form:
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password2')

            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=password).save()
            login(request, user)
            return redirect('/')


def search_product(request):
    if request.method == 'POST':
        get_product = request.POST.get('search_product')

        searched_product = Product.objects.filter(pr_name__iregex=get_product)

        if searched_product:
            context = {'products': searched_product}

            return render(request, 'result.html', context)
        else:
            return redirect('/')


# Функция выхода из аккаунта
def logout_view(request):
    logout(request)
    return redirect('/')


# Функция добавления товара в корзину
def to_cart(request, pk):
    if request.method == 'POST':
        product = Product.objects.get(id=pk)
        if 1 <= int(request.POST.get('pr_count')) <= product.pr_count:
            Cart.objects.create(user_id=request.user.id,
                                user_product=product,
                                user_pr_count=int(request.POST.get('pr_count'))).save()
            return redirect('/')


# Функция удаления товара из корзины
def del_from_cart(request, pk):
    product_to_del = Product.objects.get(id=pk)
    Cart.objects.filter(user_product=product_to_del).delete()

    return redirect('/cart')


# Отображение корзины
def cart(request):
    user_cart = Cart.objects.filter(user_id=request.user.id)

    product_ids = [p.user_product.id for p in user_cart]
    product_counts = [p.user_product.pr_count for p in user_cart]
    user_pr_counts = [p.user_pr_count for p in user_cart]

    totals = [round(t.user_product.pr_price * t.user_pr_count, 2) for t in user_cart]
    text = (f'Новый заказ!\n\n'
            f'Клиент: {User.objects.get(id=request.user.id).email}\n\n')


    if request.method == 'POST':
        for i in range(len(product_ids)):
            product = Product.objects.get(id=product_ids[i])
            product.pr_count = product_counts[i] - user_pr_counts[i]
            product.save(update_fields=['pr_count'])

        for t in user_cart:
            text += (f'Товар: {t.user_product}\n'
                     f'Количество: {t.user_pr_count}\n'
                     f'------------------------------------------\n')

        text += f'Итого: ${round(sum(totals, 2))}'
        bot.send_message(6775701667, text)
        user_cart.delete()
        return redirect('/')

    context = {'cart': user_cart, 'total': round(sum(totals, 2))}
    return render(request, 'cart.html', context)
