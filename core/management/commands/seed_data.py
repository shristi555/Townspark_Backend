from django.core.management.base import BaseCommand
from core.models import Category, Department, Badge


class Command(BaseCommand):
    help = 'Seeds the database with initial categories, departments, and badges'

    def handle(self, *args, **options):
        self.stdout.write('Seeding categories...')
        self.seed_categories()
        
        self.stdout.write('Seeding departments...')
        self.seed_departments()
        
        self.stdout.write('Seeding badges...')
        self.seed_badges()
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!'))

    def seed_categories(self):
        categories = [
            {"id": "road", "name": "Road Maintenance", "icon": "car_repair", "description": "Issues related to roads, potholes, etc.", "order": 1},
            {"id": "garbage", "name": "Garbage & Waste", "icon": "delete", "description": "Issues related to garbage collection and waste management", "order": 2},
            {"id": "sewage", "name": "Sewage & Drains", "icon": "water_drop", "description": "Issues related to sewage and drainage systems", "order": 3},
            {"id": "electricity", "name": "Electricity", "icon": "bolt", "description": "Issues related to electrical infrastructure", "order": 4},
            {"id": "streetlight", "name": "Street Light", "icon": "lightbulb", "description": "Issues related to street lighting", "order": 5},
            {"id": "water", "name": "Water Supply", "icon": "water", "description": "Issues related to water supply", "order": 6},
            {"id": "traffic", "name": "Traffic", "icon": "traffic", "description": "Issues related to traffic management", "order": 7},
            {"id": "graffiti", "name": "Graffiti & Vandalism", "icon": "format_paint", "description": "Issues related to graffiti and vandalism", "order": 8},
            {"id": "parks", "name": "Parks & Gardens", "icon": "park", "description": "Issues related to parks and public gardens", "order": 9},
            {"id": "other", "name": "Other", "icon": "more_horiz", "description": "Other miscellaneous issues", "order": 10},
        ]
        
        for cat_data in categories:
            Category.objects.update_or_create(
                id=cat_data['id'],
                defaults=cat_data
            )
        
        self.stdout.write(f'  Created/updated {len(categories)} categories')

    def seed_departments(self):
        departments = [
            {"id": "public-works", "name": "Public Works", "icon": "construction", "description": "Handles infrastructure and public utilities"},
            {"id": "sanitation", "name": "Sanitation", "icon": "delete", "description": "Handles garbage collection and sanitation"},
            {"id": "traffic", "name": "Traffic Management", "icon": "traffic", "description": "Handles traffic management and road safety"},
            {"id": "parks", "name": "Parks & Recreation", "icon": "park", "description": "Handles parks and recreational facilities"},
            {"id": "utilities", "name": "Utilities", "icon": "bolt", "description": "Handles electricity, water, and other utilities"},
            {"id": "housing", "name": "Housing", "icon": "home", "description": "Handles housing-related issues"},
            {"id": "environment", "name": "Environment", "icon": "eco", "description": "Handles environmental issues"},
        ]
        
        for dept_data in departments:
            Department.objects.update_or_create(
                id=dept_data['id'],
                defaults=dept_data
            )
        
        self.stdout.write(f'  Created/updated {len(departments)} departments')

    def seed_badges(self):
        badges = [
            {"id": "first-report", "name": "First Report", "icon": "emoji_events", "description": "Reported your first issue", "criteria": {"issues_posted": 1}},
            {"id": "community-hero", "name": "Community Hero", "icon": "military_tech", "description": "Reported 10 issues", "criteria": {"issues_posted": 10}},
            {"id": "active-citizen", "name": "Active Citizen", "icon": "star", "description": "Reported 50 issues", "criteria": {"issues_posted": 50}},
            {"id": "influencer", "name": "Influencer", "icon": "trending_up", "description": "Received 100 upvotes on your issues", "criteria": {"uplifts_received": 100}},
            {"id": "problem-solver", "name": "Problem Solver", "icon": "build", "description": "Had 5 issues resolved", "criteria": {"issues_resolved": 5}},
            {"id": "ten-resolved", "name": "10 Issues Resolved", "icon": "verified", "description": "Had 10 issues resolved", "criteria": {"issues_resolved": 10}},
        ]
        
        for badge_data in badges:
            Badge.objects.update_or_create(
                id=badge_data['id'],
                defaults=badge_data
            )
        
        self.stdout.write(f'  Created/updated {len(badges)} badges')
