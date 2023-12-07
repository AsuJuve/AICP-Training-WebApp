import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from ...models import Problem, Category


class Command(BaseCommand):
    help = 'Populate Django models from CSV file'

    def handle(self, *args, **options):
        self.stdout.write('Populating models from CSV...')

        csv_file_path = settings.BASE_DIR / 'training' / 'data' / 'problems_data.csv'

        problems_created = 0

        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                contest = int(row['contest'])
                index = row['problem_index']
                difficulty = float(row['problem_difficulty'])
                number_solutions = int(row['problem_solved_count'])

                # Create or get the Problem instance
                problem, created = Problem.objects.get_or_create(
                    contest=contest,
                    index=index,
                    difficulty=difficulty,
                    number_solutions=number_solutions
                )

                problems_created += 1

                # Now, handle the categories
                for category_name in row.keys():
                    if category_name.startswith('problem_category_') and row[category_name] == '1':
                        # Extract category name from the field
                        category_slug = category_name.replace('problem_category_', '')
                        category_slug = category_slug.replace('_', ' ')
                        category = Category.objects.get(name=category_slug)

                        problem.categories.add(category)

                self.stdout.write(f'Problems created or updated: {problems_created}')

        self.stdout.write(self.style.SUCCESS('Populating models completed!'))
