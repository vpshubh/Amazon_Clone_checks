# Store App Admin (store/admin.py)
from django.contrib import admin
from .models import Category, Product, ProductImage, ProductSpecification, Review, Cart, CartItem

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('user', 'title', 'content', 'rating', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'featured', 'created_at')
    list_filter = ('featured', 'parent')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category', 'price', 'is_on_sale', 'sale_price', 'in_stock', 'rating', 'featured')
    list_filter = ('is_on_sale', 'in_stock', 'featured', 'category')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductSpecificationInline, ReviewInline]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description', 'full_description')
        }),
        ('Pricing', {
            'fields': ('price', 'regular_price', 'sale_price', 'is_on_sale')
        }),
        ('Inventory', {
            'fields': ('in_stock', 'stock_qty')
        }),
        ('Display Options', {
            'fields': ('featured',)
        }),
        ('Statistics', {
            'fields': ('rating', 'review_count'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Make rating and review_count read-only as they're calculated from reviews
        return ['rating', 'review_count']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text', 'is_main', 'created_at')
    list_filter = ('is_main',)
    search_fields = ('product__name', 'alt_text')

@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'value')
    search_fields = ('product__name', 'name', 'value')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'title', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'content')
    readonly_fields = ('created_at',)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'total_items', 'subtotal', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'session_id')
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'saved_for_later', 'subtotal')
    list_filter = ('saved_for_later', 'created_at')
    search_fields = ('cart__user__username', 'product__name')