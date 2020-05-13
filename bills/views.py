from django.shortcuts import render, redirect

import json
from django.template.loader import render_to_string
from django.core.mail import send_mail,EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from .models import Transactions, Group, GroupMembers,Balance, Profile, Invite
from .forms import Bill_CreateForm, Bill_EditForm, Group_CreateForm, ProfileForm, UserForm, Add_new_members_form, Member_SignUpForm
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
import re, math
from django.db.models import Q
from django.contrib import messages
from django.db import transaction

import json



@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, ('Your profile was successfully updated!'))
            return redirect('profile_view')
        else:
            messages.error(request, ('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        if not hasattr(request.user, 'profile'):
            profile_form = ProfileForm(instance=None)
            return render(request, 'registration/profile.html', {
                            'user_form': user_form,
                            'profile_form': profile_form
                        })

        profile_form = ProfileForm(instance=request.user.profile)
        return render(request, 'registration/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })




class profile_view(TemplateView):
    template_name = 'registration/profile_view.html'


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })


@login_required(redirect_field_name='accounts/login')
def add_bills_home(request, id=None):
    grpname = GroupMembers.objects.filter(Q(group_name=id))
    users_list = []
    group_instance = Group.objects.get(id=id)
    for i in grpname:
        users_list.append(i)
    context = {'users':users_list}

    if request.method == 'POST':
        form = Bill_CreateForm(context,request.POST)  # users_list
        if form.is_valid():
            trans = Transactions()
            trans.bill_type = form.cleaned_data['bill_type']
            trans.amount = form.cleaned_data['amount']
            trans.added_by = request.user
            trans.added_to = Group.objects.get(Q(pk=id))
            trans.share_with = form.cleaned_data['share_with']
            trans.save()
            balances(trans.id,form.cleaned_data['share_with'], form.cleaned_data['amount'], form.cleaned_data['bill_type'], request.user)
            form = Bill_CreateForm(context)
            messages.success(request, 'Your bill was added successfully!')
            return render(request, 'bills/create_bill.html', {'form':form})
        else:
            messages.warning(request, 'Your bill was unable to add, Please try again!')
            return render(request, 'bills/create_bill.html', {'form':form})
    else:
        form = Bill_CreateForm(context)

    return render(request, 'bills/create_bill.html', {'form':form})


#  load users of the groups based on the group name
def load_users(request):
    group_id = request.GET.get('group')
    users = GroupMembers.objects.filter(Q(group_name=group_id))
    return render(request, 'bills/users_list.html', {'users': users})



def balances(id, user_list, amount, bill_type, paid_by):
    t = Transactions.objects.get(pk = id)
    bal = Balance()
    num_of_shares = len(user_list)
    due_each = float(amount)/num_of_shares

    if bill_type.lower() == 'rent':
        for u in user_list:
            bal = Balance()
            bal.transaction = t
            bal.due_amount = due_each
            bal.paid_amount = 0
            bal.shared_with = user_list
            bal.user_name = User.objects.get(id=u)
            bal.paid_by = paid_by.username
            bal.bill_type = bill_type
            bal.save()
    else:
        if str(paid_by.id) in user_list:
            bal.transaction = t
            bal.due_amount = due_each * (-(num_of_shares - 1))
            bal.paid_amount = amount
            bal.shared_with = user_list
            bal.user_name = paid_by
            bal.paid_by = paid_by.username
            bal.bill_type = bill_type
            bal.save()
        else:
            bal.transaction = t
            bal.due_amount = -amount
            bal.paid_amount = amount
            bal.shared_with = user_list
            bal.user_name = paid_by
            bal.paid_by = paid_by.username
            bal.bill_type = bill_type
            bal.save()

        for u in user_list:
            if paid_by.id != int(u):
                bal = Balance()
                bal.transaction = t
                bal.due_amount = due_each
                bal.paid_amount = 0
                bal.shared_with = user_list
                bal.user_name = User.objects.get(id=u)
                bal.paid_by = paid_by.username
                bal.bill_type = bill_type
                bal.save()


def index_balances(request):
    if request.user.is_anonymous:
        print('came here')
        return HttpResponseRedirect('accounts/login')
    user = User.objects.get(pk=request.user.id)
    context = {}
    bal = Balance.objects.filter(user_name=user)
    total_due = 0
    paid_amt = 0
    for i in bal:
        paid_amt += round(i.paid_amount,2)
        total_due += round(i.due_amount,2)
    context['paid_amt'] = paid_amt
    context['due_amt'] = total_due

    return render(request, 'index.html', {'context':context})


def balance_list(request, id=None):
    user = User.objects.get(pk=id)
    context = {}
    bal = Balance.objects.filter(user_name=user)
    total_due = 0
    for i in bal:
        context[i.id] = {
                         'Bill type': i.bill_type,
                         'Added on': i.purchase_date,
                         'Due amount' : round(i.due_amount,2) ,
                         'transaction':i.transaction
                          }
        total_due += i.due_amount

    context['total'] = {'Total Due': round(total_due,2)}
    return render(request, 'bills/balance_list.html',{'context':context})


def view_balance(request, id=None):
    trans = Transactions.objects.get(pk=id)
    context = {}
    bal = Balance.objects.get(Q(transaction=id) & Q(user_name=request.user))
    shared_with = list(int(k) for k in re.findall(r'[1-9]+', bal.shared_with))
    shared = ''
    for user in shared_with:
        shared += str(User.objects.get(pk=int(user)))
        shared += ', '
    shared = shared[:len(shared)-2]
    context = {'bill_type':trans.bill_type, 'paid_by':trans.added_by, 'amount':trans.amount, 'shared':shared, 'due':bal.due_amount, 'trans_id':id}
    return render(request, 'bills/view_balance.html', {'context':context})

def balance_details(request, id=None):
    user = User.objects.get(pk=id)
    context = {}
    bal = Balance.objects.filter(user_name=user)
    total_due = 0
    for i in bal:
        shared = ', '.join(k for k in re.findall(r'[a-zA-Z]+', i.shared_with))
        context[i.id] = {'Paid by': i.paid_by,
                         'Shared with': shared,
                         'Bill type': i.bill_type,
                         'Added on': i.purchase_date,
                         'Paid amount': round(i.paid_amount,2),
                         'Due amount' : round(i.due_amount,2) ,
                         'transaction':i.transaction
                        }
        total_due += i.due_amount

    context['total'] = {'Total Due': round(total_due,2)}


    return render(request, 'bills/balance_details.html', {'context':context})


def transaction_edit(request, id=None):
    trans = Transactions.objects.get(pk=id)
    print(trans)
    print(trans.added_to)
    users_list = []
    group_members = GroupMembers.objects.filter(Q(group_name=trans.added_to))
    for i in group_members:
        users_list.append(i)
    context = {'users':users_list}
    print(group_members)
    if request.method == 'POST':
        form = Bill_EditForm(context, request.POST, instance=trans)
        if form.is_valid():
            added_by = request.user #User.objects.get(username=form.cleaned_data['added_by'])
            form.cleaned_data['added_by'] = added_by.id
            form.save()
            balances_update(request,trans.id,form.cleaned_data['share_with'], form.cleaned_data['amount'], form.cleaned_data['bill_type'], request.user)
            context = {'message':'Transaction has been updated!'}
            return render(request,  'bills/transaction_edit.html', context)
    else:
        form = Bill_EditForm(context, instance=trans)


    return render(request, 'bills/transaction_edit.html', {'form':form})


def balances_update(request,id, user_list, amount, bill_type, paid_by):
    t = Transactions.objects.get(pk = id)
    old_bal = Balance.objects.filter(transaction__id=id)
    old_bal.delete()
    bal = Balance()
    num_of_shares = len(user_list)
    due_each = float(amount)/num_of_shares

    if bill_type.lower() == 'rent':
        for u in user_list:
            bal = Balance()
            bal.transaction = t
            bal.due_amount = due_each
            bal.paid_amount = 0
            bal.shared_with = user_list
            bal.user_name = User.objects.get(pk=int(u))
            bal.paid_by = paid_by.username
            bal.bill_type = bill_type
            bal.save()
    else:
        if str(paid_by.pk) in user_list:
            bal.transaction = t
            bal.due_amount = due_each * (-(num_of_shares - 1))
            bal.paid_amount = amount
            bal.shared_with = user_list
            bal.user_name = paid_by
            bal.paid_by = paid_by.username
            bal.bill_type = bill_type
            bal.save()
        else:
            bal.transaction = t
            bal.due_amount = -amount
            bal.paid_amount = amount
            bal.shared_with = user_list
            bal.user_name = paid_by
            bal.paid_by = paid_by.username
            bal.bill_type = bill_type
            bal.save()
        for u in user_list:
            if paid_by.pk != int(u):
                bal = Balance()
                bal.transaction = t
                bal.due_amount = due_each
                bal.paid_amount = 0
                bal.shared_with = user_list
                bal.user_name = User.objects.get(pk=int(u))
                bal.paid_by = paid_by.username
                bal.bill_type = bill_type
                bal.save()




def delete_transaction(request, id):
    t = Transactions.objects.get(pk=id)
    if request.POST:
        if 'delete' in request.POST:
            t.delete()
            context = {'message':'Transaction '+t.bill_type+' has been deleted!'}
            return render(request, 'bills/transaction_delete.html', context)
    return render(request, 'bills/transaction_delete.html')


def group_create(request):
    if request.POST:
        new_group_form = Group_CreateForm(request.POST)
        if new_group_form.is_valid():
            if Group.objects.filter(group_name=new_group_form.cleaned_data['group_name']).exists():
                messages.warning(request, 'This group name has been already taken')
                return redirect('group_create')
            new_group_form.save()
            new_group = Group.objects.get(group_name=new_group_form.cleaned_data['group_name'])
            group_members = GroupMembers()
            group_members.members = request.user
            group_members.save()
            group_members.group_name.add(new_group)
            messages.success(request, ('Your group was successfully created!'))
            return redirect('group_create')
    else:
        new_group_form = Group_CreateForm(request.POST)
    return render(request, 'bills/create_group.html', {'form':new_group_form})


def group_list_view(request, id=None):
    group_list = Group.objects.filter(groupmembers__members=id)
    context = {}

    for grp in group_list:
        grp1 = Group.objects.get(group_name=grp)
        context[grp1.id] = grp1.group_name
    return render(request,'bills/group_list.html', {'groups':context})


def group_list_bill(request, id):
    group_list = Group.objects.filter(groupmembers__members=id)
    context = {}

    for grp in group_list:
        grp1 = Group.objects.get(group_name=grp)
        context[grp1.id] = grp1.group_name
    return render(request,'bills/group_list_bill.html', {'groups':context})

def group_members_list_view(request, id=None):
    grp = Group.objects.get(pk=id)
    grp_list = GroupMembers.objects.filter(group_name=grp)
    context = {}
    for member in grp_list:
        context[member.members.id] = member.members.username
    return render(request,'bills/group_members_list.html', {'members':context, 'group':grp})


def remove_members(request, id=None):
    g_m = Group.objects.get(pk=id)
    g_m2 = GroupMembers.objects.filter(Q(group_name=g_m), Q(members=request.user))
    context = {}
    if request.POST:
        if 'delete' in request.POST:
            g_m2.delete()
    for member in g_m2:
        context['members'] = member.members.username
    context['group'] = g_m
    return render(request, 'bills/remove_members.html', context)


def add_members(request, id=None):
    group = Group.objects.get(pk=id)
    print(group)
    #group_mbrs.group_name = g_m

    if request.POST:
        form = Add_new_members_form(request.POST)
        if form.is_valid():
            print('Yes', form.cleaned_data['member_email'])
            to_email = form.cleaned_data['member_email']
            from_email = settings.EMAIL_HOST_USER
            subject = 'Your friend '+ str(request.user) +' has invited you to join ShareBills'
            text_content = 'Strong email'
            msg_html = render_to_string('bills/email_invitation.html')
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(msg_html, 'text/html')
            msg.send()

            invite_obj = Invite()
            invite_obj.group_id = id
            invite_obj.receiver_email= to_email
            invite_obj.save()

    else:
        form = Add_new_members_form()

    return render(request, 'bills/add_members.html', {'form':form})


def group_user_signup(request):
    if request.POST:
        form = Member_SignUpForm(request.POST)
        if form.is_valid():
            if Invite.objects.filter(Q(receiver_email=form.cleaned_data['email'])).exists():
                form.save()
                return redirect('login')
            else:
                messages.warning(request,('Please mention the email address that you received invitation'))
                return render(request, 'registration/group_user_registration.html', {'form':form})
    else:
        form = Member_SignUpForm()
    return render(request, 'registration/group_user_registration.html', {'form':form})
