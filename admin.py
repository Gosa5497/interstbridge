from django.contrib import admin
from .models import (
    Store, Product, Employee, Transaction, Manage, HasA, CheckTransaction,
    EmployeePhoneNo, UserProfile, WorkAt
)
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'total_amount', 'date')  # Ensure 'id' exists
    search_fields = ('id', 'total_amount')  # Ensure 'id' exists
    list_filter = ('date',)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'serial_number', 'produced_date', 'price', 'category', 'quantity', 'manufacturer')
    search_fields = ('name', 'serial_number', 'model', 'category')
    list_filter = ('produced_date', 'category')
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'work_date', 'capacity', 'address')  # Ensure 'id' exists
    search_fields = ('name', 'address', 'id')  # Ensure 'id' exists
    list_filter = ('work_date',)
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'id', 'last_name', 'date_of_joining', 'role')  # Ensure 'id' exists
    search_fields = ('first_name', 'last_name', 'role')
    list_filter = ('date_of_joining', 'role')
@admin.register(CheckTransaction)
class CheckTransactionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'transaction', 'date')
    search_fields = ('employee__first_name', 'employee__last_name', 'transaction__id')
    list_filter = ('date',)
@admin.register(Manage)
class ManageAdmin(admin.ModelAdmin):
    list_display = ('product', 'employee')
@admin.register(HasA)
class HasAAdmin(admin.ModelAdmin):
    list_display = ('product', 'store')
    search_fields = ('product__name', 'store__name')
@admin.register(EmployeePhoneNo)
class EmployeePhoneNoAdmin(admin.ModelAdmin):
    list_display = ('employee', 'phone_number')
    search_fields = ('employee__first_name', 'employee__last_name', 'phone_number')
@admin.register(WorkAt)
class WorkAtAdmin(admin.ModelAdmin):
    list_display = ('employee', 'store')
    search_fields = ('employee__first_name', 'employee__last_name', 'store__name')
    list_filter = ('start_date', 'end_date')
from .models import TransactionRequest
@admin.register(TransactionRequest)
class TransactionRequestAdmin(admin.ModelAdmin):
    list_display = ('user','store', 'product', 'quantity', 'status', 'created_at')
    list_filter = ('status','store', 'product')
    search_fields = ('user__username', 'product__name', 'store__name')
    ordering = ('-created_at',)