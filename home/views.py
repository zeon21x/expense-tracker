from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate ,logout
from django.contrib.auth import login as dj_login
from django.contrib.auth.models import User
from .models import Addmoney_info,UserProfile
from django.contrib.sessions.models import Session
from django.core.paginator import Paginator, EmptyPage , PageNotAnInteger
from django.db.models import Sum
from django.http import JsonResponse
import datetime
from django.utils import timezone
from django.db.models import Sum
from django.views.decorators.csrf import csrf_protect
import time
import csv
import json
from django.core.paginator import Paginator
from .models import Addmoney_info
from datetime import date, timedelta

# Create your views here.
def home(request):
    if request.session.has_key('is_logged'):
        return redirect('/index')
    return render(request,'home/login.html')
   # return HttpResponse('This is home')
def index(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        addmoney_info = Addmoney_info.objects.filter(user=user).order_by('-Date')
        paginator = Paginator(addmoney_info , 4)
        page_number = request.GET.get('page')
        page_obj = Paginator.get_page(paginator,page_number)
        # Calculate total expense for the last 30 days
        todays_date = datetime.date.today()
        one_month_ago = todays_date - datetime.timedelta(days=5000)
        total_expense = addmoney_info.filter(add_money='Expense', Date__gte=one_month_ago).aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_income = addmoney_info.filter(add_money='Income', Date__gte=one_month_ago).aggregate(Sum('quantity'))['quantity__sum'] or 0
        current_income = total_expense+total_income
        context = {
            # 'add_info' : addmoney_info,
           'page_obj' : page_obj,
           'total_expense': total_expense,
           'total_income' : total_income,
           'current_income':current_income,
        }
    #if request.session.has_key('is_logged'):
        return render(request,'home/index.html',context)
    return redirect('home')
    #return HttpResponse('This is blog')
def expense(request):
    if request.session.has_key('is_logged'):
        todays_date = datetime.date.today()
        one_month_ago = todays_date - datetime.timedelta(days=30)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)

        # Get all income and expense transactions for the user
        addmoney_info = Addmoney_info.objects.filter(
            user=user1,
            Date__gte=one_month_ago,
            Date__lte=todays_date
        )

        # Use Django's Sum aggregation to get the total expense.
        # This is more efficient than a Python loop.
        total_expense = addmoney_info.filter(add_money='Expense').aggregate(Sum('quantity'))['quantity__sum']

        # Handle the case where there are no expenses (the sum would be None)
        if total_expense is None:
            total_expense = 0

        # Pass the calculated total expense to the template in a context dictionary
        context = {
            'total_expense': total_expense,
        }
        
        return render(request, 'home/index.html', context)
    
    return redirect('home')

        
def register(request):
    return render(request,'home/register.html')
    #return HttpResponse('This is blog')
def password(request):
    return render(request,'home/password.html')

def charts(request):
    return render(request,'home/charts.html')
def search(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        fromdate = request.GET['fromdate']
        todate = request.GET['todate']
        addmoney = Addmoney_info.objects.filter(user=user, Date__range=[fromdate,todate]).order_by('-Date')
        return render(request,'home/tables.html',{'addmoney':addmoney})
    return redirect('home')
def tables(request):
    if request.session.has_key('is_logged'):
        user_id = request.session["user_id"]
        user = User.objects.get(id=user_id)
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        addmoney = Addmoney_info.objects.filter(user=user).order_by('-Date')
        return render(request,'home/tables.html',{'addmoney':addmoney})
    return redirect('home')
def addmoney(request):
    return render(request,'home/addmoney.html')

def profile(request):
    if request.session.has_key('is_logged'):
        return render(request,'home/profile.html')
    return redirect('/home')

def profile_edit(request,id):
    if request.session.has_key('is_logged'):
        add = User.objects.get(id=id)
        # user_id = request.session["user_id"]
        # user1 = User.objects.get(id=user_id)
        return render(request,'home/profile_edit.html',{'add':add})
    return redirect("/home")

# def profile_update(request,id):
#     if request.session.has_key('is_logged'):
#         if request.method == "POST":
#             user = User.objects.get(id=id)
#             user.first_name = request.POST["fname"]
#             user.last_name = request.POST["lname"]
#             user.email = request.POST["email"]
#             user.userprofile.Savings = request.POST["Savings"]
#             user.userprofile.income = request.POST["income"]
#             user.userprofile.profession = request.POST["profession"]
#             user.userprofile.save()
#             user.save()
#             return redirect("/profile")
#     return redirect("/home")   
def profile_update(request, id):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            user = User.objects.get(id=id)
            user.first_name = request.POST.get("fname", "")
            user.last_name = request.POST.get("lname", "")
            user.email = request.POST.get("email", "")
            user.userprofile.Savings = request.POST.get("Savings", 0)
            user.userprofile.income = request.POST.get("income", 0)
            user.userprofile.profession = request.POST.get("profession", "")

            # ✅ Handle profile image upload
            if 'profile_image' in request.FILES:
                user.userprofile.profile_image = request.FILES['profile_image']

            user.userprofile.save()
            user.save()
            return redirect("/profile")
    return redirect("/home")
def handleSignup(request):
    if request.method =='POST':
            # get the post parameters
            uname = request.POST["uname"]
            fname=request.POST["fname"]
            lname=request.POST["lname"]
            email = request.POST["email"]
            profession = request.POST['profession']
            Savings = request.POST['Savings']
            income = request.POST['income']
            pass1 = request.POST["pass1"]
            pass2 = request.POST["pass2"]
            profile = UserProfile(Savings = Savings,profession=profession,income=income)
            # check for errors in input
            if request.method == 'POST':
                try:
                    user_exists = User.objects.get(username=request.POST['uname'])
                    messages.error(request," Username already taken, Try something else!!!")
                    return redirect("/register")    
                except User.DoesNotExist:
                    if len(uname)>15:
                        messages.error(request," Username must be max 15 characters, Please try again")
                        return redirect("/register")
            
                    if not uname.isalnum():
                        messages.error(request," Username should only contain letters and numbers, Please try again")
                        return redirect("/register")
            
                    if pass1 != pass2:
                        messages.error(request," Password do not match, Please try again")
                        return redirect("/register")
            
            # create the user
            user = User.objects.create_user(uname, email, pass1)
            user.first_name=fname
            user.last_name=lname
            user.email = email
            # profile = UserProfile.objects.all()

            user.save()
            # p1=profile.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request," Your account has been successfully created")
            return redirect("/")
    else:
        return HttpResponse('404 - NOT FOUND ')
    return redirect('/login')

# def handlelogin(request):
#     if request.method =='POST':
#         # get the post parameters
#         loginuname = request.POST["loginuname"]
#         loginpassword1=request.POST["loginpassword1"]
#         user = authenticate(username=loginuname, password=loginpassword1)
#         if user is not None:
#             dj_login(request, user)
#             request.session['is_logged'] = True
#             user = request.user.id 
#             request.session["user_id"] = user
#             messages.success(request, " Successfully logged in")
#             return redirect('/index')
#         else:
#             messages.error(request," Invalid Credentials, Please try again")  
#             return redirect("/")  
#     return HttpResponse('404-not found')
@csrf_protect
def handleloginpage(request):
    return render(request, 'login.html')


# ---------- Handle Login with 3-Attempt Limit + 1-Min Timeout ----------

def handlelogin(request):
    if request.method == 'POST':
        loginuname = request.POST.get("loginuname")
        loginpassword1 = request.POST.get("loginpassword1")

        # Initialize session counters if not already set
        if 'login_attempts' not in request.session:
            request.session['login_attempts'] = 0
        if 'lockout_time' not in request.session:
            request.session['lockout_time'] = None

        lockout_time = request.session.get('lockout_time')
        current_time = time.time()

        # --- LOCKOUT CHECK: render timeout page ---
        if lockout_time and current_time < lockout_time:
            remaining = int(lockout_time - current_time)
            # Render a dedicated timeout page with countdown
            return render(request, 'home/timeout.html', {'remaining': remaining})

        # Authenticate user
        user = authenticate(username=loginuname, password=loginpassword1)

        if user is not None:
            # Reset counters on successful login
            dj_login(request, user)
            request.session['is_logged'] = True
            request.session['user_id'] = user.id
            request.session['login_attempts'] = 0
            request.session['lockout_time'] = None
            messages.success(request, "Successfully logged in")
            return redirect('/index')

        else:
            # Increment failed attempts
            request.session['login_attempts'] += 1
            remaining_attempts = 3 - request.session['login_attempts']

            if request.session['login_attempts'] >= 3:
                # Set 1-minute lockout
                request.session['lockout_time'] = current_time + 60
                return render(request, 'home/timeout.html', {'remaining': 60})
            else:
                messages.error(request, f"Invalid credentials. {remaining_attempts} attempt(s) left.")
                return redirect('/')

    return HttpResponse('404 - Not Found')

def handleLogout(request):
        del request.session['is_logged']
        del request.session["user_id"] 
        logout(request)
        messages.success(request, " Successfully logged out")
        return redirect('home')

#add money form
# def addmoney_submission(request):
#     if request.session.has_key('is_logged'):
#         if request.method == "POST":
#             user_id = request.session["user_id"]
#             user1 = User.objects.get(id=user_id)
#             addmoney_info1 = Addmoney_info.objects.filter(user=user1).order_by('-Date')
#             add_money = request.POST["add_money"]
#             quantity = request.POST["quantity"]
#             Date = request.POST["Date"]
#             Category = request.POST["Category"]
#             add = Addmoney_info(user = user1,add_money=add_money,quantity=quantity,Date = Date,Category= Category)
#             add.save()
#             paginator = Paginator(addmoney_info1, 4)
#             page_number = request.GET.get('page')
#             page_obj = Paginator.get_page(paginator,page_number)
#             context = {
#                 'page_obj' : page_obj
#                 }
#             return render(request,'home/index.html',context)
#     return redirect('/index')

# def addmoney_submission(request):
#     if request.session.has_key('is_logged'):
#         if request.method == "POST":
#             user_id = request.session["user_id"]
#             user1 = User.objects.get(id=user_id)

#             add_money = request.POST["add_money"]
#             quantity = request.POST["quantity"]
#             Date = request.POST["Date"]
#             Category = request.POST["Category"]

#             # --- CORRECTION STARTS HERE ---
#             # Convert quantity to a float
#             try:
#                 quantity = float(quantity)
#             except (ValueError, TypeError):
#                 # Handle cases where quantity is not a valid number
#                 messages.error(request, "Please enter a valid amount.")
#                 return redirect('/addmoney')

#             # If the transaction is an expense, convert the quantity to a negative number
#             if add_money == 'Expense':
#                 quantity = -quantity
#             # --- CORRECTION ENDS HERE ---

#             add = Addmoney_info(
#                 user=user1,
#                 add_money=add_money,  # Note: This field is now redundant but kept for consistency
#                 quantity=quantity,
#                 Date=Date,
#                 Category=Category
#             )
#             add.save()

#             # The rest of the code is for rendering the page
#             addmoney_info1 = Addmoney_info.objects.filter(user=user1).order_by('-Date')
#             paginator = Paginator(addmoney_info1, 4)
#             page_number = request.GET.get('page')
#             page_obj = Paginator.get_page(paginator, page_number)
            
#             context = {
#                 'page_obj': page_obj
#             }
#             messages.success(request, "Transaction added successfully!")
#             return render(request, 'home/index.html', context)
#     return redirect('/index')
# def addmoney_update(request,id):
#     if request.session.has_key('is_logged'):
#         if request.method == "POST":
#             add  = Addmoney_info.objects.get(id=id)
#             add .add_money = request.POST["add_money"]
#             add.quantity = request.POST["quantity"]
#             add.Date = request.POST["Date"]
#             add.Category = request.POST["Category"]
#             add .save()
#             return redirect("/index")
#     return redirect("/home")   

def addmoney_submission(request):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            user_id = request.session["user_id"]
            user1 = User.objects.get(id=user_id)
            add_money = request.POST["add_money"]
            quantity = request.POST["quantity"]
            Date = request.POST["Date"]
            Category = request.POST["Category"]

            try:
                quantity = float(quantity)
            except (ValueError, TypeError):
                messages.error(request, "Please enter a valid amount.")
                return redirect('/addmoney')

            if add_money == 'Expense':
                quantity = -quantity

            add = Addmoney_info(
                user=user1,
                add_money=add_money,
                quantity=quantity,
                Date=Date,
                Category=Category
            )
            add.save()
            messages.success(request, "Transaction added successfully!")
            return redirect('/index')
    return redirect('/home')
    
# --- (Rest of your views file) ---

def addmoney_update(request,id):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            add = Addmoney_info.objects.get(id=id)
            add.add_money = request.POST["add_money"]
            add.quantity = request.POST["quantity"]
            add.Date = request.POST["Date"]
            add.Category = request.POST["Category"]
            add.save()
            messages.success(request, "Transaction updated successfully!")
            return redirect("/index")
    return redirect("/home")     

def expense_edit(request,id):
    if request.session.has_key('is_logged'):
        addmoney_info = Addmoney_info.objects.get(id=id)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        return render(request,'home/expense_edit.html',{'addmoney_info':addmoney_info})
    return redirect("/home")  

# def expense_delete(request,id):
#     if request.session.has_key('is_logged'):
#         addmoney_info = Addmoney_info.objects.get(id=id)
#         addmoney_info.delete()
#         return redirect("/index")
#     return redirect("/home")  
def expense_delete(request,id):
    if request.session.has_key('is_logged'):
        addmoney_info = Addmoney_info.objects.get(id=id)
        addmoney_info.delete()
        messages.success(request, "Transaction deleted successfully!")
        return redirect("/index")
    return redirect("/home")

def expense_month(request):
    todays_date = datetime.date.today()
    one_month_ago = todays_date-datetime.timedelta(days=30)
    user_id = request.session["user_id"]
    user1 = User.objects.get(id=user_id)
    addmoney = Addmoney_info.objects.filter(user = user1,Date__gte=one_month_ago,Date__lte=todays_date)
    finalrep ={}

    def get_Category(addmoney_info):
        # if addmoney_info.add_money=="Expense":
        return addmoney_info.Category    
    Category_list = list(set(map(get_Category,addmoney)))

    def get_expense_category_amount(Category,add_money):
        quantity = 0 
        filtered_by_category = addmoney.filter(Category = Category,add_money="Expense") 
        for item in filtered_by_category:
            quantity+=item.quantity
        return quantity

    for x in addmoney:
        for y in Category_list:
            finalrep[y]= get_expense_category_amount(y,"Expense")

    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats(request):
    if request.session.has_key('is_logged') :
        todays_date = datetime.date.today()
        one_month_ago = todays_date-datetime.timedelta(days=30)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        addmoney_info = Addmoney_info.objects.filter(user = user1,Date__gte=one_month_ago)
        sum = 0 
        for i in addmoney_info:
            if i.add_money == 'Expense':
                sum=sum+i.quantity
        addmoney_info.sum = sum
        sum1 = 0 
        for i in addmoney_info:
            if i.add_money == 'Income':
                sum1 =sum1+i.quantity
        addmoney_info.sum1 = sum1
        x= user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
    
        y = addmoney_info.sum1 + addmoney_info.sum
        z = addmoney_info.sum1 + addmoney_info.sum
        if x<0:
            messages.warning(request,'Your expenses exceeded your savings')
            x = 0
        if x>0:
            y = 0
        addmoney_info.x = abs(x)
        addmoney_info.y = abs(y)
        addmoney_info.z = abs(z)
        return render(request,'home/stats.html',{'addmoney':addmoney_info})

# def expense_week(request):
#     todays_date = datetime.date.today()
#     one_week_ago = todays_date-datetime.timedelta(days=7)
#     user_id = request.session["user_id"]
#     user1 = User.objects.get(id=user_id)
#     addmoney = Addmoney_info.objects.filter(user = user1,Date__gte=one_week_ago,Date__lte=todays_date)
#     finalrep ={}

#     def get_Category(addmoney_info):
#         return addmoney_info.Category
#     Category_list = list(set(map(get_Category,addmoney)))


#     def get_expense_category_amount(Category,add_money):
#         quantity = 0 
#         filtered_by_category = addmoney.filter(Category = Category,add_money="Expense") 
#         for item in filtered_by_category:
#             quantity+=item.quantity
#         return quantity

#     for x in addmoney:
#         for y in Category_list:
#             finalrep[y]= get_expense_category_amount(y,"Expense")

#     return JsonResponse({'expense_category_data': finalrep}, safe=False) 

def expense_week(request):
    todays_date = datetime.date.today()
    one_week_ago = todays_date - datetime.timedelta(days=7)
    
    user_id = request.session.get("user_id")
    if not user_id:
        return JsonResponse({'error': 'User not logged in'}, status=401)

    user1 = User.objects.get(id=user_id)

    # ✅ Filter only last 7 days expenses
    addmoney = Addmoney_info.objects.filter(
        user=user1,
        Date__gte=one_week_ago,
        Date__lte=todays_date,
        add_money="Expense"  # Ensure only expense records
    )

    # If no data found
    if not addmoney.exists():
        return JsonResponse({'expense_category_data': {}}, safe=False)

    # ✅ Aggregate total expense per category
    expense_data = (
        addmoney.values('Category')
        .annotate(total_amount=Sum('quantity'))
        .order_by('Category')
    )

    # ✅ Convert queryset to dictionary
    finalrep = {item['Category']: item['total_amount'] for item in expense_data}

    return JsonResponse({'expense_category_data': finalrep}, safe=False)
    
def weekly(request):
    if request.session.has_key('is_logged') :
        todays_date = datetime.date.today()
        one_week_ago = todays_date-datetime.timedelta(days=7)
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        addmoney_info = Addmoney_info.objects.filter(user = user1,Date__gte=one_week_ago)
        sum = 0 
        for i in addmoney_info:
            if i.add_money == 'Expense':
                sum=sum+i.quantity
        addmoney_info.sum = sum
        sum1 = 0 
        for i in addmoney_info:
            if i.add_money == 'Income':
                sum1 = sum1 + i.quantity
            # if i.add_money == 'Income':
            #     sum1 =sum1+i.quantity
        addmoney_info.sum1 = sum1
        x= user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
        # y= user1.userprofile.Savings+addmoney_info.sum1 - addmoney_info.sum
        y= addmoney_info.sum1   #change line by me
        a= addmoney_info.sum1 + addmoney_info.sum
        z= a
        if x<0:
            messages.warning(request,'Your expenses exceeded your savings')
            x = 0
        if x>0:
            y = 0
        addmoney_info.x = abs(x)
        addmoney_info.y = abs(y)
        addmoney_info.z = abs(z)
    return render(request,'home/weekly.html',{'addmoney_info':addmoney_info})

def check(request):
    if request.method == 'POST':
        user_exists = User.objects.filter(email=request.POST['email'])
        messages.error(request,"Email not registered, TRY AGAIN!!!")
        return redirect("/reset_password")

def info_year(request):
    todays_date = datetime.date.today()
    one_week_ago = todays_date-datetime.timedelta(days=30*12)
    user_id = request.session["user_id"]
    user1 = User.objects.get(id=user_id)
    addmoney = Addmoney_info.objects.filter(user = user1,Date__gte=one_week_ago)
    finalrep ={}

    def get_Category(addmoney_info):
        return addmoney_info.Category
    Category_list = list(set(map(get_Category,addmoney)))


    def get_expense_category_amount(Category,add_money):
        quantity = 0 
        filtered_by_category = addmoney.filter(Category = Category,add_money="Expense") 
        for item in filtered_by_category:
            quantity+=item.quantity
        return quantity

    for x in addmoney:
        for y in Category_list:
            finalrep[y]= get_expense_category_amount(y,"Expense")

    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def info(request):
    return render(request,'home/info.html')
    


def export_history_csv(request):
    if not request.session.has_key('is_logged'):
        return redirect('home')

    user_id = request.session['user_id']
    user = User.objects.get(id=user_id)

    # Optional: handle date filtering if query params exist
    fromdate = request.GET.get('fromdate')
    todate = request.GET.get('todate')

    if fromdate and todate:
        transactions = Addmoney_info.objects.filter(user=user, Date__range=[fromdate, todate]).order_by('-Date')
    else:
        transactions = Addmoney_info.objects.filter(user=user).order_by('-Date')

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expense_history.csv"'

    writer = csv.writer(response)
    writer.writerow(['What you added', 'Amount', 'Category', 'Date'])

    for t in transactions:
        writer.writerow([t.add_money, t.quantity, t.Category, t.Date])

    return response    


def dashboard(request):
    user = request.user
    transactions = Addmoney_info.objects.filter(user=user).order_by('-Date')

    # Pagination
    paginator = Paginator(transactions, 10)  # 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Total expense & income
    total_expense = transactions.filter(add_money='Expense').aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_income = transactions.filter(add_money='Income').aggregate(Sum('quantity'))['quantity__sum'] or 0
    current_income = total_income + total_expense

    # Weekly expenses
    today = date.today()
    week_start = today - datetime.timedelta(days=7)  # Monday
    weekly_transactions = transactions.filter(Date__gte=week_start)
    weekly_expense = weekly_transactions.filter(add_money='Expense').values('Category').annotate(total=Sum('quantity'))
    weekly_expense_json = {item['Category']: item['total'] for item in weekly_expense}

    # Monthly expenses
    month_start = today.replace(day=1)
    monthly_transactions = transactions.filter(Date__gte=month_start)
    monthly_expense = monthly_transactions.filter(add_money='Expense').values('Category').annotate(total=Sum('quantity'))
    monthly_expense_json = {item['Category']: item['total'] for item in monthly_expense}

    # Yearly expenses
    year_start = today.replace(month=1, day=1)
    yearly_transactions = transactions.filter(Date__gte=year_start)
    yearly_expense = yearly_transactions.filter(add_money='Expense').values('Category').annotate(total=Sum('quantity'))
    yearly_expense_json = {item['Category']: item['total'] for item in yearly_expense}

    context = {
        'page_obj': page_obj,
        'total_expense': total_expense,
        'total_income': total_income,
        'current_income': current_income,
        'weekly_expense_json': json.dumps(weekly_expense_json),
        'monthly_expense_json': json.dumps(monthly_expense_json),
        'yearly_expense_json': json.dumps(yearly_expense_json),
    }

    return render(request, 'home/dashboard.html', context)

# def dashboard(request):
#     if not request.session.get('is_logged'):
#         return redirect('home')

#     user = User.objects.get(id=request.session['user_id'])
#     addmoney_info = Addmoney_info.objects.filter(user=user).order_by('-Date')
#     paginator = Paginator(addmoney_info, 10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     # Calculate total income, expense, balance
#     total_expense = sum([abs(x.quantity) for x in addmoney_info if x.add_money=='Expense'])
#     total_income = sum([x.quantity for x in addmoney_info if x.add_money=='Income'])
#     current_income = total_income - total_expense 

#     # Weekly
#     one_week_ago = datetime.date.today() - datetime.timedelta(days=7)
#     weekly_data = addmoney_info.filter(Date__gte=one_week_ago, add_money='Expense')
#     weekly_expense = {}
#     for item in weekly_data:
#         weekly_expense[item.Category] = weekly_expense.get(item.Category, 0) + abs(item.quantity)

#     # Monthly
#     one_month_ago = datetime.date.today() - datetime.timedelta(days=30)
#     monthly_data = addmoney_info.filter(Date__gte=one_month_ago, add_money='Expense')
#     monthly_expense = {}
#     for item in monthly_data:
#         monthly_expense[item.Category] = monthly_expense.get(item.Category, 0) + abs(item.quantity)

#     # Yearly
#     one_year_ago = datetime.date.today() - datetime.timedelta(days=365)
#     yearly_data = addmoney_info.filter(Date__gte=one_year_ago, add_money='Expense')
#     yearly_expense = {}
#     for item in yearly_data:
#         yearly_expense[item.Category] = yearly_expense.get(item.Category, 0) + abs(item.quantity)

#     context = {
#         'page_obj': page_obj,
#         'total_expense': total_expense,
#         'total_income': total_income,
#         'current_income': current_income,
#         'weekly_expense_json': json.dumps(weekly_expense),
#         'monthly_expense_json': json.dumps(monthly_expense),
#         'yearly_expense_json': json.dumps(yearly_expense),
#     }

#     return render(request, 'home/dashboard.html', context)
