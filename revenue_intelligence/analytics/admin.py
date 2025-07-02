from django.contrib import admin

from .models import Account
from .models import Contact
from .models import Opportunity


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "id")
    search_fields = ("name", "id")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("full_name", "title", "email", "account")
    search_fields = ("first_name", "last_name", "email", "account__name")
    list_select_related = ("account",)


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("name", "account", "amount", "stage", "probability", "close_date")
    search_fields = ("name", "account__name")
    list_filter = ("stage", "lead_source")
    list_select_related = ("account",)
