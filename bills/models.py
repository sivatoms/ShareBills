from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField('Phone number',max_length=14, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

class Group(models.Model):
    group_name = models.CharField('Group name', max_length=50)

    def __str__(self):
        return self.group_name


class GroupMembers(models.Model):
    group_name = models.ManyToManyField(Group)
    members = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.members.username


class Transactions(models.Model):
    bill_type = models.CharField('Bill type',max_length=200)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    added_to = models.ForeignKey(Group, on_delete=models.CASCADE)
    purchase_date = models.DateField(auto_now=True)
    amount = models.FloatField(default=0)
    share_with = models.CharField(max_length=255)
    def __str__(self):
        return self.bill_type


class Balance(models.Model):
    transaction = models.ForeignKey(Transactions, on_delete=models.CASCADE)
    bill_type = models.CharField('Bill type', max_length=50, null=False, blank=False, default='Grocery type')
    user_name = models.ForeignKey(User,on_delete=models.CASCADE)
    paid_by = models.CharField(max_length=150, null=True, blank=True)
    paid_amount = models.FloatField('You Spent', default=0,null=True, blank=True)
    due_amount = models.FloatField('You Owe', default=0,null=True, blank=True)
    shared_with = models.CharField("Shared With", max_length=250)
    purchase_date = models.DateField(auto_now=True)

    def __unicode__(self):
        return self.user_name


class Invite(models.Model):
    receiver_email = models.EmailField("Recipient Email", max_length=254)
    group_id = models.IntegerField(null=False, blank=False)
