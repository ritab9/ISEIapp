from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.dispatch import receiver
from .models import Teacher


# TODO Not Used
# create Profile instead of Teacher, for options for other type of users
# or, have a group for each user type and have a new sign in when the group is attached at sign in
# and the Profile is created and matched based on that sign in
#@receiver(post_save, sender=User)
#def create_teacher(sender, instance, created, **kwargs):
#	if created:
#		group = Group.objects.get(name='teacher')
#		instance.groups.add(group)
#		Teacher.objects.create(user=instance, first_name=instance.first_name, last_name = instance.last_name)
			
