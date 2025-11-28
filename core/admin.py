from django.contrib import admin
from .models import Category, Department, Badge


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'icon', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'icon', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'icon']
    search_fields = ['name', 'description']
