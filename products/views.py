from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def product_list(request):
    # Sample product data - in a real app, this would come from your database
    products = [
        {'id': 1, 'name': 'Health & Personal Care', 'image': 'box1_image.jpg'},
        {'id': 2, 'name': 'Electronics', 'image': 'box2_image.jpg'},
        # Add all your box categories here
    ]
    return render(request, 'product_list.html', {'products': products})

def product_detail(request, product_id):
    # Get product details based on ID
    product = {
        'id': product_id,
        'name': f'Product {product_id} Details',
        'price': 99.99,
        'description': 'Detailed product description here'
    }
    return render(request, 'product_detail.html', {'product': product})

def cart(request):
    return render(request, 'cart.html')

def checkout(request):
    return render(request, 'checkout.html')

def account(request):
    return render(request, 'account.html')