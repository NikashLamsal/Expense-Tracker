from django.shortcuts import render , redirect
from django.shortcuts import get_object_or_404
from .models import TrackingHistory , CurrentBalance
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.models import User

from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required

# Create your views here.
 
@login_required(login_url="login_page")
def index(request):  # sourcery skip: assign-if-exp, introduce-default-else
 
 
    current_balance,_ = CurrentBalance.objects.get_or_create(user=request.user)

    edit_transaction = None
    edit_id = request.GET.get('edit')
    if edit_id:
        edit_transaction = get_object_or_404(TrackingHistory,id = edit_id,user=request.user)
    if request.method == "POST":

        description = request.POST.get('description')
        amount = request.POST.get('amount')


        expense_type = "CREDIT"
        if float(amount) < 0:
            expense_type = "DEBIT"

        if float(amount) == 0:
            messages.success(request, "Amount cannot be zero") 
            return redirect('/')

        # current_balance, _ = CurrentBalance.objects.get_or_create(id = 1)
        # income = 0
        # expense = 0
 
        TrackingHistory.objects.create (
            user = request.user,
            amount = amount,
            expense_type = expense_type,
            current_balance = current_balance,
            description = description )
        
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
             

    context = {
        'income' : income,
        'expense' : expense,
        'transactions' : user_transactions,
        'current_balance' : current_balance,
        'edit_transaction' : edit_transaction
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

        if float(amount) == 0:
            messages.error(request, "Amount cannot be zero")
            return redirect('/')

        expense_type = "CREDIT"
        if float(amount) < 0:
            expense_type = "DEBIT"
 
        transaction.description = description
        transaction.amount = amount
        transaction.expense_type = expense_type
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


        user = User.objects.filter(username = username)
        if user.exists():
           messages.success(request,"username already taken")
           return redirect('/register/')
        
        user = User.objects.create(
            username = username,
            first_name = first_name,
            last_name = last_name
        )
        user.set_password(password)
        user.save()
        messages.success(request,"Account Created")
        return redirect('/login/')

        




    return render(request,"register.html" )

