from django.contrib import admin
from .models import User, VendorProfile, StaffMember
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('is_vendor', 'is_staff_member')}),
    )

admin.site.register(VendorProfile)
admin.site.register(StaffMember)
