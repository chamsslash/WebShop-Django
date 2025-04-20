from carts.models import Cart


def get_user_carts(request):
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user).select_related('product')#берем именно из релатиона обьект(именно связанный)
    
    if not request.session.session_key:
        request.session.create()#автоматом и сешн кей появляется
    return Cart.objects.filter(session_key=request.session.session_key).select_related('product')