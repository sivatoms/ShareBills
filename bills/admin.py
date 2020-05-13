from django.contrib import admin

from .models import Group, GroupMembers, Transactions, Balance, Profile, Invite
# Register your models here.

admin.site.register(Group)
admin.site.register(GroupMembers)
admin.site.register(Transactions)
admin.site.register(Balance)
admin.site.register(Profile)
admin.site.register(Invite)
