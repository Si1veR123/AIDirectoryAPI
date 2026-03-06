import kagglehub
import csv
import os
from django.core.management.base import BaseCommand

from tool.models import Tool, Developer, Domain, Accessibility, ContextWindow

FILE_NAME = "AI_Landscape_19k_Tools_2026.csv"
DATASET_NAME = "harshlakhani2005/ai-tool-directory-2026-10000-real-world-tools"

class Command(BaseCommand):
    help = "Load initial dataset into database"

    def handle(self, *args, **kwargs):
        path = kagglehub.dataset_download(DATASET_NAME)
        file_path = os.path.join(path, FILE_NAME)

        self.stdout.write("Clearing existing data...")

        Tool.objects.all().delete()
        Developer.objects.all().delete()
        Domain.objects.all().delete()
        Accessibility.objects.all().delete()
        ContextWindow.objects.all().delete()

        self.stdout.write("Reading CSV...")

        with open(file_path, newline='', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))  # Load once into memory

        # --------------------------------------------------
        # 1️⃣ Collect unique related field values
        # --------------------------------------------------

        developers = {row['Developer'] for row in reader}
        domains = {row['Primary_Domain'] for row in reader}
        accessibilities = {row['Accessibility'] for row in reader}
        context_windows = {row['Context_Window'] for row in reader}

        self.stdout.write("Bulk creating related objects...")

        Developer.objects.bulk_create(
            [Developer(name=name) for name in developers],
            ignore_conflicts=True
        )
        Domain.objects.bulk_create(
            [Domain(name=name) for name in domains],
            ignore_conflicts=True
        )
        Accessibility.objects.bulk_create(
            [Accessibility(name=name) for name in accessibilities],
            ignore_conflicts=True
        )
        ContextWindow.objects.bulk_create(
            [ContextWindow(name=name) for name in context_windows],
            ignore_conflicts=True
        )

        # --------------------------------------------------
        # 2️⃣ Build lookup dictionaries
        # --------------------------------------------------

        developer_map = {
            obj.name: obj for obj in Developer.objects.all()
        }
        domain_map = {
            obj.name: obj for obj in Domain.objects.all()
        }
        accessibility_map = {
            obj.name: obj for obj in Accessibility.objects.all()
        }
        context_window_map = {
            obj.name: obj for obj in ContextWindow.objects.all()
        }

        # --------------------------------------------------
        # 3️⃣ Bulk create Tools
        # --------------------------------------------------

        self.stdout.write("Bulk creating tools...")

        tools = []

        for row in reader:
            tools.append(
                Tool(
                    ai_name=row['AI_Name'],
                    developer=developer_map[row['Developer']],
                    release_year=int(row['Release_Year']) if row['Release_Year'] else None,
                    intelligence_type=row['Intelligence_Type'],
                    primary_domain=domain_map[row['Primary_Domain']],
                    key_functionality=row['Key_Functionality'],
                    pricing_model=row['Pricing_Model'],
                    api_availability=row['API_Availability'],
                    context_window=context_window_map[row['Context_Window']],
                    accessibility=accessibility_map[row['Accessibility']],
                    popularity_votes=int(row['Popularity_Votes']) if row['Popularity_Votes'] else 0,
                    website_url=row['Website_URL'],
                )
            )

        # Batch insert (very important for memory + speed)
        Tool.objects.bulk_create(tools, batch_size=1000)

        self.stdout.write(self.style.SUCCESS("Dataset loaded successfully!"))