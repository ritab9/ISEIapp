
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from users.models import UserProfile, Teacher
from selfstudy.models import SelfStudy_TeamMember

class Command(BaseCommand):
    help = "Create UserProfile for existing users"

    def handle(self, *args, **options):
        users_with_profiles = 0
        teachers_updated = 0

        print("running")

        for user in User.objects.all():
            # Skip users who already have profiles
            if UserProfile.objects.filter(user=user).exists():
                continue

            # Create a profile
            profile = UserProfile.objects.create(user=user)

            # Check if the user is a Teacher and set the school
            teacher = getattr(user, "teacher", None)
            if teacher and teacher.school:
                profile.school = teacher.school
                teachers_updated += 1

            # Check if the user is a TeamMember and set the school
            team_member = SelfStudy_TeamMember.objects.filter(user=user).first()
            if team_member:
                profile.school = team_member.team.selfstudy.accreditation.school
                user.groups.add(Group.objects.get(name="coordinating_team"))

            # Save the profile
            profile.save()
            users_with_profiles += 1

            print(profile)

        self.stdout.write(f"Created profiles for {users_with_profiles} users.")
        self.stdout.write(f"Updated school information for {teachers_updated} teachers.")
