from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.conf import settings
from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import (
    User,
    Role,
    RefreshToken,
    EventLog,
    UserNotification
)
from django.contrib.admin.sites import AlreadyRegistered

admin.site.register(Role)
admin.site.register(RefreshToken)
admin.site.register(EventLog)
admin.site.register(UserNotification)

try:

    @admin.register(Group)
    class GroupAdmin(admin.ModelAdmin):
        list_display = ["id", "name"]

except AlreadyRegistered:
    pass


class UserCreationForm(forms.ModelForm):
    """ User creation class definition.
    Allows creation of new users in the django admin section \
        using custom user model
    """

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password Confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("user_id", "email", "phone_no")

    def clean_password2(self):
        """get and validate password"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 != password2:
            raise forms.ValidationError("Passwords dont't match")
        return password2

    def save(self, commit=True):
        """set  and save user to database"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """User Change Form class definition"""

    password = ReadOnlyPasswordHashField()

    class Meta:
        """Meta data needed for change form"""

        model = User
        fields = (
            "email",
            "phone_no",
            "password",
            "is_active",
            "is_admin",
        )

    def clean_password(self):
        """validated and return password"""
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    """User Admin class definition"""

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        "user_id",
        "email",
    )
    list_filter = ("is_admin",)
    fieldsets = (
        (None, {"fields": ("email", "password", "phone_no", "user_id")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_admin",
                    "groups",
                    "roles",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "phone_no", "password1", "password2"),
            },
        ),
    )

    search_fields = ("email", "phone_no")
    ordering = (
        "email",
        "phone_no",
    )
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
