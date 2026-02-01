from django.shortcuts import render , redirect
from django.shortcuts import get_object_or_404
from .models import TrackingHistory , CurrentBalance
from django.db.models import Sum
from django.contrib import messages
# Create your views here.
 

def index(request):  # sourcery skip: assign-if-exp, introduce-default-else
 

    current_balance,_ = CurrentBalance.objects.get_or_create(id = 1)

    edit_transaction = None
    edit_id = request.GET.get('edit')
    if edit_id:
        edit_transaction = get_object_or_404(TrackingHistory,id = edit_id)
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
 
        TrackingHistory.objects.create(
            amount = amount,
            expense_type = expense_type,
            current_balance = current_balance,
            description = description)
        
        total = TrackingHistory.objects.aggregate(total=Sum('amount'))['total'] or 0

        current_balance.current_balance = total
        current_balance.save()
        return redirect('/')


    income = 0
    expense = 0

    for tracking_history in TrackingHistory.objects.all():
         
        if tracking_history.expense_type == "CREDIT":
              income += tracking_history.amount
        else:
             expense += tracking_history.amount
             

    context = {
        'income' : income,
        'expense' : expense,
        'transactions' : TrackingHistory.objects.all(),
        'current_balance' : current_balance,
        'edit_transaction' : edit_transaction
    }

    return render(request, 'index.html' , context)


def delete_transaction(request , id):
    tracking_history = TrackingHistory.objects.filter(id = id)
    if tracking_history.exists():

        current_balance,_ = CurrentBalance.objects.get_or_create(id = 1)
        tracking_history = tracking_history[0]
        current_balance.current_balance = current_balance.current_balance - tracking_history.amount
        current_balance.save()



    tracking_history.delete()
    return redirect('/')

def update_transaction(request, id):

    transaction = TrackingHistory.objects.get(id = id)
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


        total = TrackingHistory.objects.aggregate(total=Sum('amount'))['total'] or 0

        current_balance,_ = CurrentBalance.objects.get_or_create(id=1)
        current_balance.current_balance = total
        current_balance.save()

        messages.success(request, "Transaction updated successfully")
        return redirect('/')
    return redirect('/')