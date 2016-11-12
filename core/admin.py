from django.contrib import admin

from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from core.models import addict_user
# Register your models here.

class AddictInline(admin.StackedInline):
    model = addict_user
    can_delete = False
    verbose_name_plural = 'adduser'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (AddictInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(team)
