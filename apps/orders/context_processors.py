from .models import Cart

def cart_item_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        return {
            "cart_item_count": cart.items.count() if cart else 0
        }
    else:
        return {"cart_item_count": 0}
