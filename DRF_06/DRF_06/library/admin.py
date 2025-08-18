from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Book, CustomUser


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass


class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ('userid', 'firstname', 'email', 'gender', 'notified')
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'userid',
                    'firstname',
                    'email',
                    'gender',
                    'notified',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'userid',
                    'firstname',
                    'email',
                    'gender',
                    'notified',
                    'password1',
                    'password2',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
    )
    search_fields = ('userid', 'firstname', 'email')
    ordering = ('userid',)


admin.site.register(CustomUser, CustomUserAdmin)
