# Store App Views (store/views.py - expanded)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Category, Product, Review, Cart, CartItem
from .forms import ReviewForm, CartAddProductForm, ProductSearchForm

def home(request):
    """Home page view with featured products, categories and deals"""
    featured_products = Product.objects.filter(featured=True)[:8]
    featured_categories = Category.objects.filter(featured=True)[:4]
    deal_products = Product.objects.filter(is_on_sale=True)[:3]
    
    context = {
        'title': 'Amazon Clone - Home',
        'featured_products': featured_products,
        'featured_categories': featured_categories, 
        'deal_products': deal_products
    }
    return render(request, 'store/home.html', context)

def product_list(request, category_slug=None):
    """Display products with optional category filter and search"""
    category = None
    search_form = ProductSearchForm(request.GET)
    products = Product.objects.all()
    
    # Filter by category if provided
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Apply search filters if form is valid
    if search_form.is_valid():
        data = search_form.cleaned_data
        
        # Search query
        if data['search']:
            products = products.filter(
                Q(name__icontains=data['search']) | 
                Q(description__icontains=data['search'])
            )
        
        # Category filter from form
        if data['category']:
            category = get_object_or_404(Category, slug=data['category'])
            products = products.filter(category=category)
        
        # Price range filter
        if data['min_price']:
            products = products.filter(price__gte=data['min_price'])
        if data['max_price']:
            products = products.filter(price__lte=data['max_price'])
        
        # Rating filter
        if data['rating'] and int(data['rating']) > 0:
            products = products.filter(rating__gte=data['rating'])
        
        # Sorting
        if data['sort'] == 'price_low':
            products = products.order_by('price')
        elif data['sort'] == 'price_high':
            products = products.order_by('-price')
        elif data['sort'] == 'rating':
            products = products.order_by('-rating')
        elif data['sort'] == 'newest':
            products = products.order_by('-created_at')
        else:  # Featured or default
            products = products.order_by('-featured', '-rating')
    
    context = {
        'title': category.name if category else 'All Products',
        'category': category,
        'products': products,
        'search_form': search_form,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, pk):
    """Display product details and related products"""
    product = get_object_or_404(Product, pk=pk)
    cart_product_form = CartAddProductForm()
    
    # Get related products from same category
    related_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]
    
    # Handle review form submission
    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            # Check if user already reviewed this product
            existing_review = Review.objects.filter(product=product, user=request.user).first()
            
            if existing_review:
                # Update existing review
                existing_review.title = review_form.cleaned_data['title']
                existing_review.content = review_form.cleaned_data['content']
                existing_review.rating = review_form.cleaned_data['rating']
                existing_review.save()
            else:
                # Create new review
                review = review_form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                
                # Update product rating and review count
                update_product_rating(product)
                
            return redirect('store:product_detail', pk=product.pk)
    else:
        review_form = ReviewForm()
    
    # Check if user already reviewed this product
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()
        if user_review:
            review_form = ReviewForm(instance=user_review)
    
    context = {
        'product': product,
        'related_products': related_products,
        'cart_product_form': cart_product_form,
        'review_form': review_form,
        'user_review': user_review,
    }
    return render(request, 'store/product_detail.html', context)

@login_required
def add_review(request, product_id):
    """Add or update a product review"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Check if user already has a review for this product
            try:
                review = Review.objects.get(user=request.user, product=product)
                # Update existing review
                review.title = form.cleaned_data['title']
                review.content = form.cleaned_data['content']
                review.rating = form.cleaned_data['rating']
                review.save()
            except Review.DoesNotExist:
                # Create new review
                review = form.save(commit=False)
                review.user = request.user
                review.product = product
                review.save()
            
            # Update product rating
            update_product_rating(product)
            
            return redirect('store:product_detail', pk=product.id)
    
    return redirect('store:product_detail', pk=product.id)

def update_product_rating(product):
    """Helper function to update product rating based on reviews"""
    reviews = product.reviews.all()
    if reviews.exists():
        avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
        product.rating = round(avg_rating, 1)
        product.review_count = reviews.count()
    else:
        product.rating = 0
        product.review_count = 0
    product.save()

# Cart views
def get_or_create_cart(request):
    """Helper function to get or create user cart"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # For anonymous users, use session ID
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_id=session_key)
    
    return cart

@require_POST
def cart_add(request, product_id):
    """Add a product to cart"""
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        quantity = cd['quantity']
        update = cd['update']
        
        # Try to get existing cart item
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            if update:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
            cart_item.saved_for_later = False  # Ensure it's in the active cart
            cart_item.save()
        except CartItem.DoesNotExist:
            CartItem.objects.create(cart=cart, product=product, quantity=quantity)
        
        # If AJAX request, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'{product.name} added to your cart',
                'cart_count': cart.total_items
            })
        else:
            return redirect('store:cart')
    
    # If form invalid or not AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'error',
            'message': 'Error adding product to cart'
        }, status=400)
    else:
        return redirect('store:product_detail', pk=product_id)

def cart_remove(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    
    # Security check to ensure user only modifies their own cart
    if cart_item.cart == cart:
        cart_item.delete()
    
    # If AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Item removed from cart',
            'cart_count': cart.total_items,
            'cart_subtotal': cart.subtotal
        })
    else:
        return redirect('store:cart')

def cart_update(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    
    # Security check to ensure user only modifies their own cart
    if cart_item.cart == cart:
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0 and quantity <= 9:
            cart_item.quantity = quantity
            cart_item.save()
    
    # If AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Cart updated',
            'item_subtotal': cart_item.subtotal,
            'cart_subtotal': cart.subtotal
        })
    else:
        return redirect('store:cart')

def save_for_later(request, item_id):
    """Save cart item for later"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    
    # Security check to ensure user only modifies their own cart
    if cart_item.cart == cart:
        cart_item.saved_for_later = True
        cart_item.save()
    
    # If AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Item saved for later',
            'cart_count': cart.total_items,
            'cart_subtotal': cart.subtotal
        })
    else:
        return redirect('store:cart')

def move_to_cart(request, item_id):
    """Move saved item back to cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    
    # Security check to ensure user only modifies their own cart
    if cart_item.cart == cart:
        cart_item.saved_for_later = False
        cart_item.save()
    
    # If AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Item moved to cart',
            'cart_count': cart.total_items,
            'cart_subtotal': cart.subtotal
        })
    else:
        return redirect('store:cart')

def cart_view(request):
    """View cart contents and saved items"""
    cart = get_or_create_cart(request)
    
    # Get active cart items
    cart_items = cart.items.filter(saved_for_later=False)
    
    # Get saved-for-later items
    saved_items = cart.items.filter(saved_for_later=True)
    
    # Get recommended products based on cart items
    recommended_products = []
    if cart_items:
        # Get categories of products in cart
        cart_categories = set(item.product.category for item in cart_items)
        # Get products from those categories that aren't in the cart
        cart_product_ids = [item.product.id for item in cart_items]
        recommended_products = Product.objects.filter(
            category__in=cart_categories
        ).exclude(
            id__in=cart_product_ids
        ).order_by('-rating')[:4]
    
    context = {
        'cart_items': cart_items,
        'saved_items': saved_items,
        'cart_subtotal': cart.subtotal,
        'recommended_products': recommended_products,
    }
    return render(request, 'store/cart.html', context)
""" 
def category_detail(request, slug):
    # Dummy response to avoid the error
    return render(request, 'store/category_detail.html', {'slug': slug}) """