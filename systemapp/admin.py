from django.contrib import admin
from .models import Farm,UserProfile,Cattle,HealthCase,Practitioner,IssueReport,Order

admin.site.register(Farm)
admin.site.register(Cattle)
admin.site.register(HealthCase)
admin.site.register(Practitioner)
admin.site.register(IssueReport)
admin.site.register(Order)
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'farm',
        'approval_status',
        'ai_verified',
        'account_blocked'
    )

    list_filter = (
        'approval_status',
        'account_blocked'
    )

    search_fields = (
        'user__username',
        'farm_name'
    )