from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
import random
from shop.models import Category, Supplier, Product, Customer, Order, OrderItem, Review


class Command(BaseCommand):
    help = "Seed demo data (1000+ records)"

    def add_arguments(self, parser):
        parser.add_argument("--products", type=int, default=200)
        parser.add_argument("--customers", type=int, default=300)
        parser.add_argument("--orders", type=int, default=400)

    @transaction.atomic
    def handle(self, *args, **opts):
        fake = Faker()

        # Categories
        categories = []
        for name in [
            "Electronics",
            "Books",
            "Clothing",
            "Home",
            "Sports",
            "Toys",
            "Beauty",
        ]:
            categories.append(
                Category.objects.get_or_create(
                    name=name, defaults={"slug": name.lower().replace(" ", "-")}
                )[0]
            )
        self.stdout.write(self.style.SUCCESS(f"Categories: {len(categories)}"))

        # Suppliers
        suppliers = []
        for _ in range(20):
            suppliers.append(
                Supplier.objects.create(
                    name=fake.company(),
                    email=fake.company_email(),
                    phone=fake.phone_number(),
                )
            )
        self.stdout.write(self.style.SUCCESS(f"Suppliers: {len(suppliers)}"))

        # Products
        products = []
        for i in range(opts["products"]):
            cat = random.choice(categories)
            sup = random.choice(suppliers)
            p = Product.objects.create(
                sku=f"P-{i+1:05d}",
                name=fake.catch_phrase(),
                description=fake.paragraph(nb_sentences=3),
                category=cat,
                supplier=sup,
                price=round(random.uniform(5, 500), 2),
                stock=random.randint(0, 500),
                is_active=random.choice([True, True, True, False]),
            )
            products.append(p)
        self.stdout.write(self.style.SUCCESS(f"Products: {len(products)}"))

        # Customers
        customers = []
        for _ in range(opts["customers"]):
            customers.append(
                Customer.objects.create(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.unique.email(),
                    city=fake.city(),
                )
            )
        self.stdout.write(self.style.SUCCESS(f"Customers: {len(customers)}"))

        # Orders + Items
        orders = []
        for _ in range(opts["orders"]):
            c = random.choice(customers)
            order = Order.objects.create(
                customer=c,
                status=random.choice(
                    [Order.Status.NEW, Order.Status.PAID, Order.Status.SHIPPED]
                ),
            )
            orders.append(order)
            # 1..5 items
            for __ in range(random.randint(1, 5)):
                prod = random.choice(products)
                qty = random.randint(1, 4)
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    quantity=qty,
                    unit_price=prod.price,
                )
        self.stdout.write(self.style.SUCCESS(f"Orders: {len(orders)}"))

        # Reviews (random subset)
        created_reviews = 0
        for cust in random.sample(customers, k=min(200, len(customers))):
            for prod in random.sample(products, k=random.randint(1, 5)):
                if not Review.objects.filter(customer=cust, product=prod).exists():
                    Review.objects.create(
                        customer=cust,
                        product=prod,
                        rating=random.randint(1, 5),
                        comment=fake.sentence(nb_words=12),
                    )
                    created_reviews += 1

        total = (
            len(categories)
            + len(suppliers)
            + len(products)
            + len(customers)
            + len(orders)
            + created_reviews
        )
        self.stdout.write(
            self.style.SUCCESS(f"Seed complete. Rows created/updated: {total}+")
        )
