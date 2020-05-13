from .models import Profile, Group, GroupMembers, Invite
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def add_group_member(sender, instance, created, **kwargs):
    if created:
        email = instance.email        
        if Invite.objects.filter(Q(receiver_email=email)).exists():
            invite_obj = Invite.objects.get(Q(receiver_email=email))
            print(invite_obj.receiver_email, invite_obj.group_id)
            group = Group.objects.get(Q(id=invite_obj.group_id))
            group_members = GroupMembers()
            group_members.members = instance
            group_members.save()
            group_members.group_name.add(group)
            invite_obj.delete()
        else:
            group_members = GroupMembers()
            group_members.members = instance
            group_members.save()
            group_members.group_name.add(22)
