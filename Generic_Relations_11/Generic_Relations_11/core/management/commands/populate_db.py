import random
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from products.models import Category, Product, Supplier
from services.models import ServiceType, Service, ServiceProvider
from comments.models import Comment
from ratings.models import Rating

User = get_user_model()


class Command(BaseCommand):
    help = 'Populates the database with fake data.'

    def add_arguments(self, parser):
        parser.add_argument('num_records', type=int, help='Number of records to create')

    def handle(self, *args, **options):
        fake = Faker()
        num_records = options['num_records']

        self.stdout.write("Populating database...")

        with transaction.atomic():
            # Clear existing data to start fresh
            self.stdout.write("Clearing old data...")
            Category.objects.all().delete()
            Product.objects.all().delete()
            Supplier.objects.all().delete()
            ServiceType.objects.all().delete()
            Service.objects.all().delete()
            ServiceProvider.objects.all().delete()
            Comment.objects.all().delete()
            Rating.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

            self.stdout.write("Creating core data...")
            # Create Users
            users = []
            for _ in range(num_records):
                users.append(
                    User(
                        username=fake.user_name(),
                        email=fake.email(),
                        password=fake.password(),
                    )
                )
            User.objects.bulk_create(users)
            self.stdout.write(self.style.SUCCESS(f"Created {len(users)} users."))

            # Create Products data
            categories = [Category(name=fake.word()) for _ in range(num_records // 10)]
            Category.objects.bulk_create(categories)
            self.stdout.write(f"Created {len(categories)} categories.")

            suppliers = [
                Supplier(
                    name=fake.company(),
                    contact_email=fake.email(),
                    phone_number=fake.phone_number(),
                    address=fake.address(),
                )
                for _ in range(num_records // 10)
            ]
            Supplier.objects.bulk_create(suppliers)
            self.stdout.write(f"Created {len(suppliers)} suppliers.")

            products = []
            if categories:
                for _ in range(num_records):
                    products.append(
                        Product(
                            name=fake.word(),
                            description=fake.text(),
                            price=fake.pydecimal(
                                left_digits=3, right_digits=2, positive=True
                            ),
                            category=random.choice(categories),
                            stock_quantity=random.randint(0, 100),
                            is_published=fake.boolean(),
                        )
                    )
                Product.objects.bulk_create(products)
            self.stdout.write(f"Created {len(products)} products.")

            # Create Services data
            service_types = [
                ServiceType(name=fake.word(), description=fake.sentence())
                for _ in range(num_records // 10)
            ]
            ServiceType.objects.bulk_create(service_types)
            self.stdout.write(f"Created {len(service_types)} service types.")

            services = []
            if service_types:
                for _ in range(num_records):
                    services.append(
                        Service(
                            name=fake.word(),
                            description=fake.text(),
                            price_per_hour=fake.pydecimal(
                                left_digits=2, right_digits=2, positive=True
                            ),
                            service_type=random.choice(service_types),
                            is_available=fake.boolean(),
                        )
                    )
                Service.objects.bulk_create(services)
            self.stdout.write(f"Created {len(services)} services.")

            # Create Generic Relations data (Comments & Ratings)
            self.stdout.write("Creating generic relations...")
            users = list(User.objects.all())
            products = list(Product.objects.all())
            services = list(Service.objects.all())

            # Create ContentType objects
            product_content_type = ContentType.objects.get_for_model(Product)
            service_content_type = ContentType.objects.get_for_model(Service)

            comments = []
            ratings = []

            for _ in range(num_records):
                # Randomly choose between a Product and a Service
                if random.choice([True, False]):
                    obj = random.choice(products)
                    content_type = product_content_type
                else:
                    obj = random.choice(services)
                    content_type = service_content_type

                comments.append(
                    Comment(
                        user=random.choice(users),
                        text=fake.paragraph(nb_sentences=3),
                        content_type=content_type,
                        object_id=obj.pk,
                    )
                )
                ratings.append(
                    Rating(
                        user=random.choice(users),
                        score=random.randint(1, 5),
                        content_type=content_type,
                        object_id=obj.pk,
                    )
                )

            Comment.objects.bulk_create(comments)
            Rating.objects.bulk_create(ratings)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {len(comments)} comments and {len(ratings)} ratings."
                )
            )

        self.stdout.write(self.style.SUCCESS('Database population complete!'))
