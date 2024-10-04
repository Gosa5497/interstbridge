from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
class WorkDate(models.Model):
    date = models.DateField(unique=True)

    def __str__(self):
        return self.date.strftime('%Y-%m-%d')

# Model for storing store information
class Store(models.Model):
    name = models.CharField(max_length=255)
    work_date = models.DateField(blank=True, null=True)
    capacity = models.IntegerField()
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Model for storing product information
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, unique=True)
    produced_date = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='product_photos/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.IntegerField(default=0)
    available_quantity = models.PositiveIntegerField(default=0)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    is_delivered = models.BooleanField(default=False) 
    def __str__(self):
        return self.name
# Model for storing employee information
class Employee(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('storekeeper', 'Storekeeper')
    ]
    role = models.CharField(max_length=255, choices=ROLE_CHOICES)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='employees')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_joining = models.DateTimeField(auto_now_add=True, editable=False)
    profile_photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Model for storing transaction information
class Transaction(models.Model):
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.id}"

# Model for managing the relationship between products and employees
class Manage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'employee')

    def __str__(self):
        return f"{self.employee} manages {self.product}"

# Model for the relationship between products and stores
class HasA(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'store')

    def __str__(self):
        return f"{self.product} at {self.store}"

# Model for checking transactions done by employees
class CheckTransaction(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True, blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'transaction')

    def __str__(self):
        return f"{self.employee} checked {self.transaction}"
# Model for storing employee phone numbers
class EmployeePhoneNo(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)

    class Meta:
        unique_together = ('employee', 'phone_number')

    def __str__(self):
        return f"{self.employee} - {self.phone_number}"

# Model for storing user profiles
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return self.user.username

# Model for the relationship between employees and stores
class WorkAt(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    end_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        unique_together = ('employee', 'store')

    def __str__(self):
        return f"{self.employee} works at {self.store}"
class TransactionRequest(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # New fields for confirmations
    user_confirmation = models.BooleanField(default=False)
    storekeeper_confirmation = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.product.name} - {self.status}'


