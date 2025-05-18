
# store/context_processors.py
from .models import Cart

def cart(request):
    """
    Context processor to make cart available to all templates
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_id=session_key)
    
    return {'cart': cart}