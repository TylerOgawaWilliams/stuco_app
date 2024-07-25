from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.forms import CustomUserCreationForm, CustomUserChangeForm
from users.models import CustomUser
from django.db.models.functions import Lower


# Register your models here.
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    readonly_fields = ("last_login",)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "last_login",
        "member_of_groups"
    )
    list_filter = (
        "groups",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "last_login",
    )
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Name Info", {"fields": ("first_name", "last_name")}),
        ("Login Info", {"fields": ("last_login",)}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    search_fields = ("email",)
    ordering = (Lower("last_name"), Lower("first_name"))

    def member_of_groups(self, obj):
        return ",".join([g.name for g in obj.groups.all()])


admin.site.register(CustomUser, CustomUserAdmin)
