# from django.contrib import admin
# from .models import Category, Supplier, Product, Customer, Order, OrderItem, Review

# # Register your models here.
# admin.site.register(Category)
# admin.site.register(Supplier)
# admin.site.register(Product)
# admin.site.register(Customer)
# admin.site.register(Order)
# admin.site.register(OrderItem)
# admin.site.register(Review)

from django.contrib import admin, messages
from django.db.models import Sum, F, Count
from django.urls import path, reverse
from django.utils.html import format_html
from django.http import HttpResponse
import csv
from django.shortcuts import redirect, render

from .models import Category, Supplier, Product, Customer, Order, OrderItem, Review
from .forms import ProductAdminForm

# -------------------------------
# Custom Admin Site (branding + custom URLs)
# -------------------------------


class ShopAdminSite(admin.AdminSite):
    site_header = "Shop Admin"
    site_title = "Shop Control Panel"
    index_title = "Welcome to the Shop Admin"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "sales-report/",
                self.admin_view(self.sales_report_view),
                name="sales-report",
            ),
        ]
        return custom + urls

    def sales_report_view(self, request):
        # Total revenue per day (last 30 days)
        from django.utils import timezone
        from django.db.models.functions import TruncDate

        qs = (
            OrderItem.objects.select_related("order")
            .annotate(day=TruncDate("order__created_at"))
            .values("day")
            .annotate(revenue=Sum(F("quantity") * F("unit_price")))
            .order_by("-day")[:30]
        )

        context = {
            "title": "Sales report (last 30 days)",
            "rows": list(qs),
            "site_header": self.site_header,
        }
        # Render simple HTML without extra template for brevity:
        rows_html = "".join(
            f"<tr><td>{r['day']}</td><td>${r['revenue'] or 0:.2f}</td></tr>"
            for r in context["rows"]
        )
        html = f"""
        <div class="container" style="padding:20px">
          <h1>{context['title']}</h1>
          <p><a href="{reverse('admin:index')}">← Back to admin</a></p>
          <table class="grp-table" style="min-width:400px">
            <thead><tr><th>Date</th><th>Revenue</th></tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>
        """
        return HttpResponse(html)


shop_admin_site = ShopAdminSite(name="shop_admin")

# -------------------------------
# Custom Filters & Actions
# -------------------------------


# ---- Custom Filters ----
class AmountRangeFilter(admin.SimpleListFilter):
    title = "Order Amount"
    parameter_name = "amount_range"

    def lookups(self, request, model_admin):
        return [
            ("low", "Below 100"),
            ("medium", "100 - 500"),
            ("high", "Above 500"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "low":
            return queryset.filter(total_amount__lt=100)
        if self.value() == "medium":
            return queryset.filter(total_amount__gte=100, total_amount__lte=500)
        if self.value() == "high":
            return queryset.filter(total_amount__gt=500)


class HasOrdersFilter(admin.SimpleListFilter):
    title = "Has orders"
    parameter_name = "has_orders"

    def lookups(self, request, model_admin):
        return [("yes", "Yes"), ("no", "No")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.annotate(n=Count("orders")).filter(n__gt=0)
        if self.value() == "no":
            return queryset.annotate(n=Count("orders")).filter(n=0)
        return queryset


@admin.action(description="Mark selected orders as PAID")
def mark_paid(modeladmin, request, queryset):
    updated = queryset.update(status=Order.Status.PAID)
    messages.success(request, f"{updated} orders marked as PAID.")


@admin.action(description="Mark selected orders as SHIPPED")
def mark_shipped(modeladmin, request, queryset):
    updated = queryset.update(status=Order.Status.SHIPPED)
    messages.success(request, f"{updated} orders marked as SHIPPED.")


@admin.action(description="Export selected orders to CSV")
def export_orders_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=orders.csv"
    writer = csv.writer(response)
    writer.writerow(["Order ID", "Customer", "Status", "Created", "Total"])
    # annotate totals per order
    totals = OrderItem.objects.values("order_id").annotate(
        total=Sum(F("quantity") * F("unit_price"))
    )
    totals_map = {t["order_id"]: t["total"] for t in totals}
    for o in queryset.select_related("customer"):
        writer.writerow(
            [o.pk, str(o.customer), o.status, o.created_at, totals_map.get(o.pk, 0)]
        )
    return response


# -------------------------------
# Inlines
# -------------------------------


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ["product"]
    fields = ("product", "quantity", "unit_price", "line_total_display")
    readonly_fields = ("line_total_display",)

    def line_total_display(self, obj):
        if obj.pk:
            return f"${obj.line_total():.2f}"
        return "-"

    line_total_display.short_description = "Line total"


# -------------------------------
# ModelAdmins
# -------------------------------


@admin.register(Category, site=shop_admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    def product_count(self, obj):
        return obj.products.count()


@admin.register(Supplier, site=shop_admin_site)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone")
    search_fields = ("name", "email")
    list_filter = ("name",)


@admin.register(Product, site=shop_admin_site)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = (
        "sku",
        "name",
        "category",
        "supplier",
        "price",
        "stock",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "category", "supplier")
    search_fields = ("sku", "name", "description")
    list_editable = ("price", "stock", "is_active")
    date_hierarchy = "created_at"
    autocomplete_fields = ["category", "supplier"]


@admin.register(Customer, site=shop_admin_site)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "city",
        "joined_at",
        "orders_link",
    )
    search_fields = ("first_name", "last_name", "email", "city")
    list_filter = (HasOrdersFilter, "city")
    date_hierarchy = "joined_at"

    def orders_link(self, obj):
        url = reverse("admin:shop_order_changelist") + f"?customer__id__exact={obj.id}"
        return format_html('<a href="{}">View orders</a>', url)

    orders_link.short_description = "Orders"


@admin.register(Order, site=shop_admin_site)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "status_colored",
        "created_at",
        "total_display",
        "refund_button",
    )
    list_filter = ("status", AmountRangeFilter, "created_at")
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]
    actions = [mark_paid, mark_shipped, export_orders_csv]
    list_select_related = ("customer",)
    search_fields = ("customer__name", "id")

    # Row-level coloring
    def status_colored(self, obj):
        color = {
            "PENDING": "orange",
            "SHIPPED": "green",
            "REFUNDED": "red",
        }.get(obj.status, "black")
        return format_html('<span style="color: {};">{}</span>', color, obj.status)

    # Object-level Refund Button
    def refund_button(self, obj):
        if obj.status != "REFUNDED":
            return format_html(
                '<a class="button" href="{}">Refund</a>', f"refund/{obj.id}"
            )
        return "Already Refunded"

    # ✅ Row-level class injection
    def get_changelist_instance(self, request):
        cl = super().get_changelist_instance(request)
        for obj in cl.result_list:
            obj.row_class = f"row-status-{obj.status}"
        return cl

    class Media:
        css = {
            "all": (
                "css/admin_row_colors.css",
            )  # you must place this file under static/css/
        }

    # Custom admin URLs
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "refund/<int:order_id>",
                self.admin_site.admin_view(self.process_refund),
                name="order-refund",
            ),
            path(
                "sales_chart/",
                self.admin_site.admin_view(self.sales_chart_view),
                name="sales-chart",
            ),
        ]
        return custom_urls + urls

        # Refund processing

    def process_refund(self, request, order_id):
        order = Order.objects.get(pk=order_id)
        order.status = "REFUNDED"
        order.save()
        self.message_user(request, f"Order {order_id} refunded successfully!")
        return redirect("..")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_total=Sum(F("items__quantity") * F("items__unit_price")))

    def total_display(self, obj):
        return f"${(obj._total or 0):.2f}"

    # Bulk Actions
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=orders.csv"
        writer = csv.writer(response)
        writer.writerow(["ID", "Customer", "Amount", "Status", "Created"])
        for order in queryset:
            writer.writerow(
                [
                    order.id,
                    order.customer,
                    order.total_amount,
                    order.status,
                    order.created_at,
                ]
            )
        return response

    export_as_csv.short_description = "Export Selected Orders to CSV"

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status="SHIPPED")
        self.message_user(request, f"{updated} orders marked as shipped")

    mark_as_shipped.short_description = "Mark Selected as Shipped"

    # Chart.js Sales Report
    def sales_chart_view(self, request):
        from django.db.models import Sum
        import json

        data = Order.objects.values("status").annotate(total=Sum("total_amount"))
        context = {
            "labels": [d["status"] for d in data],
            "values": [float(d["total"]) for d in data],
            "title": "Sales by Status",
        }
        return render(request, "admin/sales_chart.html", context)

    total_display.short_description = "Total"


@admin.register(Review, site=shop_admin_site)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "customer", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__name", "customer__email")
    autocomplete_fields = ["product", "customer"]
