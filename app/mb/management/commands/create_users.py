import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from allauth.socialaccount.models import SocialAccount
import os

class Command(BaseCommand):
    help = 'Creates users from a users.csv file, assigns them to groups, and creates social accounts'

    def handle(self, *args, **options):
        csv_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'users.csv')
        
        self.stdout.write(self.style.SUCCESS(f'Processing file {csv_file_path}'))

        # Ensure groups exist
        data_admin, created_admin = Group.objects.get_or_create(name='data_admin')
        data_contributor,created_contributor = Group.objects.get_or_create(name='data_contributor')
        
        if created_admin:
            self.stdout.write(self.style.SUCCESS('Group data_admin created'))
            
        if created_contributor:
            self.stdout.write(self.style.SUCCESS('Group data_contributor created'))
        
        with open(csv_file_path, newline='', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user, created = User.objects.get_or_create(
                    username=row['username'],
                    defaults={
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'email': row['email']
                    }
                )

                if created:
                    user.set_password(row['password'])
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully created user {user.username}'))
                else:
                    self.stdout.write(self.style.NOTICE(f'User {user.username} already exists'))

                # Assign user to groups based on CSV
                if row.get('group') == 'data_admin':
                    data_admin.user_set.add(user)
                elif row.get('group') == 'data_contributor':
                    data_contributor.user_set.add(user)

                # Create social account if not exists
                _, soc_created = SocialAccount.objects.get_or_create(
                    user=user,
                    provider='orcid',
                    uid=row['uid']
                )
                if soc_created:
                    self.stdout.write(self.style.SUCCESS(f'Social account created for {user.username}'))
                    
                else:
                    self.stdout.write(self.style.NOTICE(f'Social account already exists for {user.username}'))

        self.stdout.write(self.style.SUCCESS('All users and their social accounts have been processed.'))
