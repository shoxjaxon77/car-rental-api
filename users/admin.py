from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'full_name', 'avatar_preview', 'status')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name', 'address')
    ordering = ('-date_joined',)
    list_per_page = 25

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or "-"
    full_name.short_description = 'Full Name'

    def status(self, obj):
        if obj.is_superuser:
            return format_html('<span style="color: red;">Superuser</span>')
        elif obj.is_staff:
            return format_html('<span style="color: blue;">Staff</span>')
        return format_html('<span style="color: green;">Active</span>') if obj.is_active else 'Inactive'
    status.short_description = 'Status'

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width: 30px; height: 30px; border-radius: 50%;" />', obj.avatar.url)
        return '-'
    avatar_preview.short_description = 'Avatar'

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': (
            'first_name', 'last_name', 'email', 'phone_number', 'address', 'avatar'
        )}),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
        )}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'phone_number', 'address'),
        }),
    )
