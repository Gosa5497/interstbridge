from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.template.response import TemplateResponse
from .decorator import allow_user
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from .models import Store, Product, Employee,  TransactionRequest, Transaction, CheckTransaction, UserProfile,WorkDate
from .forms import StoreForm, TransactionRequestForm, WorkDateForm, ProductForm, EmployeeForm, UserRegistrationForm, UserProfileForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
def search_products(request):
    category = request.GET.get('category')
    products = Product.objects.filter(category__icontains=category) if category else None
    return render(request, 'myapp/product_search_results.html', {'products': products})
@login_required
def confirm_user(request, pk):
    transaction_request = get_object_or_404(TransactionRequest, pk=pk)
    if request.user == transaction_request.user:
        transaction_request.user_confirmation = True
        transaction_request.save()

        # Optionally, you can perform additional checks here if needed
        messages.success(request, 'User confirmed the transaction request.')
    else:
        messages.error(request, 'You are not authorized to confirm this request.')
    return redirect('manage_transaction_requests')
@login_required
@user_passes_test(lambda u: u.employee.role == 'storekeeper')
def confirm_storekeeper(request, pk):
    transaction_request = get_object_or_404(TransactionRequest, pk=pk)
    transaction_request.storekeeper_confirmation = True
    transaction_request.save()

    # Remove the product from the store after confirming delivery
    product = transaction_request.product
    messages.success(request, 'Storekeeper confirmed the delivery of the product.')
    return redirect('manage_transaction_requests')
@login_required
def transaction_request_details(request, pk):
    transaction_request = get_object_or_404(TransactionRequest, pk=pk)
    return render(request, 'transaction/transaction_request_details.html', {
        'request': transaction_request
    })
@login_required
def request_transaction(request):
    if request.method == 'POST':
        form = TransactionRequestForm(request.POST)
        if form.is_valid():
            transaction_request = form.save(commit=False)
            transaction_request.user = request.user
            
            # Check if the requested quantity exceeds available quantity
            product = get_object_or_404(Product, pk=transaction_request.product.pk)  # Assuming your form has a product field
            if transaction_request.quantity > product.quantity:
                messages.error(request, 'Requested quantity exceeds available stock.')
                return render(request, 'myapp/request_transaction.html', {'form': form})

            transaction_request.save()
            
            # Get the store manager
            store_manager = Employee.objects.filter(store=transaction_request.store, role='manager').first()
            
            # Check if a store manager exists
            if store_manager:
                send_request_notification_to_manager(request, transaction_request, store_manager)

            messages.success(request, 'Transaction request submitted successfully!')
            return redirect('home')  # Or redirect to a specific page
    else:
        form = TransactionRequestForm()
    return render(request, 'myapp/request_transaction.html', {'form': form})

def send_request_notification_to_manager(request, transaction_request, manager):
    subject = 'New Transaction Request'
    
    # Generate URLs for approval and rejection
    approve_url = request.build_absolute_uri(reverse('approve_transaction_request', args=[transaction_request.pk]))
    reject_url = request.build_absolute_uri(reverse('reject_transaction_request', args=[transaction_request.pk]))

    # Render the email content from the template
    message = render_to_string('transaction/transaction_request_notification.html', {
        'request': transaction_request,
        'manager': manager,
        'approve_url': approve_url,
        'reject_url': reject_url,
    })

    # Send the email
    send_mail(
        subject,
        message,
        'from@example.com',  # Replace with your sender's email
        [manager.user.email],  # The recipient's email
        html_message=message  # Optional: send as HTML email
    )

@login_required
@user_passes_test(lambda u: u.employee.role == 'manager')
def approve_transaction_request(request, pk):
    transaction_request = get_object_or_404(TransactionRequest, pk=pk)
    if transaction_request.status == 'pending':
        transaction_request.status = 'approved'
        transaction_request.save()

        # Notify the storekeeper
        storekeeper = Employee.objects.filter(store=transaction_request.store, role='storekeeper').first()
        if storekeeper:
            send_approval_notification_to_storekeeper(transaction_request, storekeeper)

        messages.success(request, 'Transaction request approved. Notification sent to storekeeper.')

    return redirect('manage_transaction_requests')

@login_required
@user_passes_test(lambda u: u.employee.role == 'manager')
def reject_transaction_request(request, pk):
    transaction_request = get_object_or_404(TransactionRequest, pk=pk)
    if transaction_request.status == 'pending':
        transaction_request.status = 'rejected'
        transaction_request.save()

        # Notify the user about the rejection
        send_rejection_notification_to_user(transaction_request)

        messages.error(request, 'Transaction request rejected. User notified.')

    return redirect('manage_transaction_requests')

def send_approval_notification_to_storekeeper(transaction_request, storekeeper):
    subject = 'Transaction Request Approved'
    message = render_to_string('transaction/transaction_request_approved.html', {
        'request': transaction_request,
        'storekeeper': storekeeper,
    })
    send_mail(
        subject,
        message,
        'from@example.com',
        [storekeeper.user.email],
        html_message=message
    )

def send_rejection_notification_to_user(transaction_request):
    subject = 'Transaction Request Rejected'
    message = render_to_string('transaction/transaction_request_rejected.html', {
        'request': transaction_request,
    })
    send_mail(
        subject,
        message,
        'from@example.com',
        [transaction_request.user.email],
        html_message=message
    )

def send_request_notification_to_storekeeper(request, storekeeper):
    subject = 'Transaction Request Approved'
    message = render_to_string('transaction/transaction_request_approved.html', {
    'request': request,
    'storekeeper': storekeeper,
})
    send_mail(subject, message, 'from@example.com', [storekeeper.user.email])
@login_required
def manage_transaction_requests(request):
    transaction_requests = TransactionRequest.objects.all().order_by('-created_at')
    return render(request, 'transaction/manage_transaction_requests.html', {'transaction_requests': transaction_requests})
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')
@login_required
def profile(request, pk):
    user_profile = get_object_or_404(UserProfile, pk=pk)
    return render(request, 'registration/profile.html', {'user_profile': user_profile})
def update_profile(request):
    # Get or create the user profile associated with the current user
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            # Redirect to the profile page with the pk of the user_profile
            return redirect('profile', pk=user_profile.pk)
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'registration/update_profile.html', {'form': form})
@login_required
def home(request):
    stores = Store.objects.all()
    products = Product.objects.all()
    employees = Employee.objects.all()
    transaction_requests = TransactionRequest.objects.all().order_by('-created_at')[:5]
    is_manager = user_has_permission(request.user, 'Managers')
    is_admin = user_has_permission(request.user, 'Admins')

    context = {
        'stores': stores,
        'products': products,
        'employees': employees,
        'transaction_requests': transaction_requests,
        'is_manager': is_manager,
        'is_admin': is_admin,
    }
    return render(request, 'myapp/home.html', context)
@login_required
def all_stores(request):
    stores = Store.objects.all()
    products = Product.objects.all()
    employees = Employee.objects.all()
    activities = CheckTransaction.objects.all().order_by('-date')[:10]
    is_manager = user_has_permission(request.user, 'Managers')
    is_admin = user_has_permission(request.user, 'Admins')
    context = {
        'stores': stores,
        'products': products,
        'employees': employees,
        'activities': activities,
        'is_manager': is_manager,
        'is_admin': is_admin,
    }
    return render(request, 'myapp/all_stores.html', context)
@login_required
def add_store(request):
    if request.method == 'POST':
        store_form = StoreForm(request.POST)
        work_date_form = WorkDateForm(request.POST)
        
        if store_form.is_valid() and work_date_form.is_valid():
            store = store_form.save()
            selected_dates = work_date_form.cleaned_data['work_dates']
            store.work_dates.set(selected_dates)
            return redirect('home')  # Redirect to the list of stores or another view
    else:
        store_form = StoreForm()
        work_date_form = WorkDateForm()
    
    return render(request, 'myapp/add_store.html', {
        'store_form': store_form,
        'work_date_form': work_date_form
    })

@login_required
def update_store(request, pk):
    store_instance = get_object_or_404(Store, pk=pk)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store_instance)
        if form.is_valid():
            form.save()
            return redirect('store-details', pk=store_instance.pk)
    else:
        form = StoreForm(instance=store_instance)
    return render(request, 'myapp/update_store.html', {'form': form, 'store': store_instance})
@login_required
def delete_store(request, pk):
    store_instance = get_object_or_404(Store, pk=pk)
    if request.method == 'POST':
        store_instance.delete()
        return redirect('all_stores')
    return render(request, 'myapp/confirm_delete.html', {'store': store_instance})

def store_details(request, pk):
    store = get_object_or_404(Store, pk=pk)
    return render(request, 'myapp/store_details.html', {'store': store})
@login_required
def employee_details(request, pk):
    employee_instance = get_object_or_404(Employee, pk=pk)
    return render(request, 'myapp/employee_details.html', {'employee': employee_instance})
@login_required
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.user = request.user
            employee.save()
            messages.success(request, 'Employee added successfully!')
            return redirect('employee-details', pk=employee.pk)
    else:
        form = EmployeeForm()
    return render(request, 'myapp/add_employee.html', {'form': form})
@login_required
def update_employee(request, pk):
    employee_instance = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee_instance)
        if form.is_valid():
            form.save()
            return redirect('employee-details', pk=employee_instance.pk)
    else:
        form = EmployeeForm(instance=employee_instance)
    return render(request, 'myapp/update_employee.html', {'form': form, 'employee': employee_instance})
@login_required
def delete_employee(request, pk):
    employee_instance = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee_instance.delete()
        return redirect('all_stores')
    return render(request, 'myapp/employee_delete.html', {'employee': employee_instance})
@login_required
def product_details(request, pk):
    product_instance = get_object_or_404(Product, pk=pk)
    return render(request, 'myapp/product_details.html', {'product': product_instance})

@login_required
def available_product_view(request, pk):
    store = get_object_or_404(Store, pk=pk)
    products = Product.objects.filter(store=store, quantity__gt=0, is_delivered=False)  # Exclude delivered products
    return render(request, 'myapp/available_product.html', {'products': products})
def available_employee_view(request,pk):
    store = get_object_or_404(Store, pk=pk)
    employees = Employee.objects.filter(store=store)
    return render(request, 'myapp/available_employee.html', {'employees': employees})
@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('all_stores')
    else:
        form = ProductForm()
    return render(request, 'myapp/add_product.html', {'form': form})

@login_required
def update_product(request, pk):
    product_instance = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product_instance)
        if form.is_valid():
            form.save()
            return redirect('product-details', pk=product_instance.pk)
    else:
        form = ProductForm(instance=product_instance)
    return render(request, 'myapp/update_product.html', {'form': form, 'product': product_instance})
@login_required
def delete_product(request, pk):
    product_instance = get_object_or_404(Product, pk=pk)
    store_instance = product_instance.store
    if request.method == 'POST':
        product_instance.delete()
        return redirect('store-details', pk=store_instance.pk)
    return render(request, 'myapp/product_delete.html', {'product': product_instance})
def user_has_permission(user, group_name):
    return user.groups.filter(name=group_name).exists()
