from django.shortcuts import render , redirect
from django.shortcuts import get_object_or_404
from .models import TrackingHistory , CurrentBalance, Category ,EmailVerificationToken
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.models import User

from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required
from datetime import date  


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.conf import settings

# Create your views here.
 
@login_required(login_url="login_page")
def index(request): 
 
 
    current_balance,_ = CurrentBalance.objects.get_or_create(user=request.user)

    edit_transaction = None
    edit_id = request.GET.get('edit')
    if edit_id:
        edit_transaction = get_object_or_404(TrackingHistory,id = edit_id,user=request.user)
    if request.method == "POST":

        description = request.POST.get('description')
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')






        expense_type = "CREDIT"
        if float(amount) < 0:
            expense_type = "DEBIT"

        if float(amount) == 0:
            messages.success(request, "Amount cannot be zero") 
            return redirect('/')

        # current_balance, _ = CurrentBalance.objects.get_or_create(id = 1)
        # income = 0
        # expense = 0
 
        category = None
        if category_id:
            category = Category.objects.filter(id=category_id, user=request.user).first()


        TrackingHistory.objects.create (
            user = request.user,
            amount = amount,
            expense_type = expense_type,
            current_balance = current_balance,
            description = description,
            category = category )
        
        total = TrackingHistory.objects.filter(user = request.user).aggregate(total=Sum('amount'))['total'] or 0

        current_balance.current_balance = total
        current_balance.save()
        return redirect('/')


    income = 0
    expense = 0
    user_transactions = TrackingHistory.objects.filter(user=request.user)
   
    for tracking_history in user_transactions:
         
        if tracking_history.expense_type == "CREDIT":
              income += tracking_history.amount
        else:
             expense += tracking_history.amount
             
    user_categories = Category.objects.filter(user=request.user)
    today = date.today()
    context = {
        'income' : income,
        'expense' : expense,
        'transactions' : user_transactions,
        'current_balance' : current_balance,
        'edit_transaction' : edit_transaction,
        'categories': user_categories,
        'today': today
    }

    return render(request, 'index.html' , context)

@login_required(login_url="login_page")
def delete_transaction(request , id):
    tracking_history = TrackingHistory.objects.filter(id = id, user = request.user)
    if tracking_history.exists():
        tracking_history = tracking_history.first()

        current_balance,_ = CurrentBalance.objects.get_or_create(user = request.user)
        # tracking_history = tracking_history[0]
        current_balance.current_balance = current_balance.current_balance - tracking_history.amount
        current_balance.save()



        tracking_history.delete()
    return redirect('/')

@login_required(login_url="login_page")
def update_transaction(request, id):

    transaction = get_object_or_404(TrackingHistory, id=id, user=request.user)
    if request.method == "POST":
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')

        if float(amount) == 0:
            messages.error(request, "Amount cannot be zero")
            return redirect('/')

        expense_type = "CREDIT"
        if float(amount) < 0:
            expense_type = "DEBIT"

        category = None
        if category_id:
            category = Category.objects.filter(id=category_id, user=request.user).first()

 
        transaction.description = description
        transaction.amount = amount
        transaction.expense_type = expense_type
        transaction.category = category

        transaction.save()


        total = TrackingHistory.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0

        current_balance,_ = CurrentBalance.objects.get_or_create(user=request.user)
        current_balance.current_balance = total
        current_balance.save()

        messages.success(request, "Transaction updated successfully")
        return redirect('/')
    return redirect('/')



def login_view(request):
    if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = User.objects.filter(username = username)
            if not user.exists():
                messages.success(request,"user not found")
                return redirect('/login/')
            user = authenticate(username = username , password = password)
            print(user)
            if not user:
                messages.success(request , "Incorrect password")

                return redirect('/login/')
            login(request , user)
            return redirect('/')

    return render(request,"login.html" )



def logout_view(request):
    logout(request)
    return redirect('/login/')



def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user = User.objects.filter(username = username)
        if user.exists():
           messages.success(request,"username already taken")
           return redirect('/register/')
        

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('/register/')
        

        user = User.objects.create(
            username = username,
            first_name = first_name,
            last_name = last_name,
            email=email,
            is_active = False

        )
        user.set_password(password)
        user.save()


        create_default_categories(user) 
        token = EmailVerificationToken.objects.create(user=user)
        current_site = get_current_site(request)
        verification_url = f"http://{current_site.domain}/verify/{token.token}/"

        try:
            html_content = render_to_string('verification_email.html', {
                'username': user.username,
                'verification_url': verification_url,
            })
            plain_text = strip_tags(html_content)

            email_msg = EmailMultiAlternatives(
                    subject='Verify your email address',
                    body=plain_text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email]
                )
            email_msg.attach_alternative(html_content, "text/html")
            email_msg.send()

            messages.success(request, "Account created! Please check your email to verify your account.")
        except Exception as e:
            print(f"Email error: {e}")
            messages.error(request, "Account created but email could not be sent.")

        return redirect('/login/')

    return render(request,"register.html" )

def verify_email(request, token):
    try:
        verification_token = EmailVerificationToken.objects.get(token=token)

        if not verification_token.is_valid():
            messages.error(request, "This verification link has expired.")
            return redirect('/login/')

        user = verification_token.user
        user.is_active = True
        user.save()

        verification_token.delete()

        messages.success(request, "Email verified successfully! You can now login.")
        return redirect('/login/')

    except EmailVerificationToken.DoesNotExist:
        messages.error(request, "Invalid verification link.")
        return redirect('/login/')



def create_default_categories(user):
    
    default_categories = [
        {'name': 'Salary', 'icon': 'fa-money-bill', 'color': '#10b981', 'type': 'INCOME'},
        {'name': 'Freelance', 'icon': 'fa-laptop', 'color': '#3b82f6', 'type': 'INCOME'},
        {'name': 'Investment', 'icon': 'fa-chart-line', 'color': '#06b6d4', 'type': 'INCOME'},
        {'name': 'Food', 'icon': 'fa-utensils', 'color': '#f59e0b', 'type': 'EXPENSE'},
        {'name': 'Transport', 'icon': 'fa-car', 'color': '#ef4444', 'type': 'EXPENSE'},
        {'name': 'Shopping', 'icon': 'fa-shopping-cart', 'color': '#8b5cf6', 'type': 'EXPENSE'},
        {'name': 'Bills', 'icon': 'fa-file-invoice', 'color': '#ec4899', 'type': 'EXPENSE'},
        {'name': 'Entertainment', 'icon': 'fa-film', 'color': '#14b8a6', 'type': 'EXPENSE'},
        {'name': 'Health', 'icon': 'fa-heart-pulse', 'color': '#f43f5e', 'type': 'EXPENSE'},
        {'name': 'Other', 'icon': 'fa-circle', 'color': '#64748b', 'type': 'EXPENSE'},
    ]
    
    for cat_data in default_categories:
        Category.objects.get_or_create(user=user, **cat_data)
        