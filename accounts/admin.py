from django.contrib import admin
from accounts.models import UserAccount,BlackListedToken, ContactSupport
# Register your models here.


admin.site.register(UserAccount)

admin.site.register(BlackListedToken)

admin.site.register(ContactSupport)