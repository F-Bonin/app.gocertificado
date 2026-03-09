from django.contrib import admin
from .models import Company, Instructor


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "cnpj", "active", "created_at")
    list_filter = ("active",)
    search_fields = ("name", "cnpj")


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "credentials", "company", "active")
    list_filter = ("active", "company")
    search_fields = ("full_name", "credentials")
