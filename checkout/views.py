from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


def checkout(request):
    """ Checkout view to handle the checkout process. """
    # Check if the bag is empty
    bag = request.session.get('bag', {})
    if not bag:
        # If the bag is empty, redirect to products page with a message
        messages.error(request, "There is nothing in your bag at the moment")
        return redirect(reverse('products'))
    
    # If the bag is not empty, create an order form
    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
    }

    # Render the checkout template with the order form
    return render(request, template, context)
