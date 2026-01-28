from django.shortcuts import render , redirect
from .models import TrackingHistory , CurrentBalance
from django.contrib import messages

# Create your views here.
def index(request):  # sourcery skip: assign-if-exp, introduce-default-else
    if request.method == "POST":
        description = request.POST.get('description')
        amount = request.POST.get('amount')


        current_balance,_ = CurrentBalance.objects.get_or_create(id = 1)
        expense_type = "CREDIT"
        if float(amount) < 0:
            expense_type = "DEBIT"

        if float(amount) == 0:
            messages.success(request, "Amount cannot be zero") 
            return redirect('/')


        current_balance, _ = CurrentBalance.objects.get_or_create(id = 1)
        income = 0
        expense = 0

        tracking_history = TrackingHistory.objects.create(
            amount = amount,
            expense_type = expense_type,
            current_balance = current_balance,
            description = description)
        current_balance.current_balance += float(tracking_history.amount)
        current_balance.save()
        return redirect('/')
    context = {
        'transactions' : TrackingHistory.objects.all()
    }

    def delete_transaction(request, id):
        tracking_history = TrackingHistory.objects.filter(id = id)

        if tracking_history.exists():
            current_balance, _ = CurrentBalance.objects.get_or_create(id = 1)
            tracking_history = tracking_history[0]
            
            current_balance.current_balance = current_balance.current_balance - tracking_history.amount

            current_balance.save()


        tracking_history.delete()
        return redirect('/')



    return render(request, 'index.html' , context)


def delete_transaction(request, id):
        tracking_history = TrackingHistory.objects.filter(id = id)

        if tracking_history.exists():
            current_balance, _ = CurrentBalance.objects.get_or_create(id = 1)
            tracking_history = tracking_history[0]
            
            current_balance.current_balance = current_balance.current_balance - tracking_history.amount

            current_balance.save()


        tracking_history.delete()
        return redirect('/')






