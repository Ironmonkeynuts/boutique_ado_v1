from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from bag.contexts import bag_contents

import stripe


def checkout(request):
    """ Checkout view to handle the checkout process. """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # Check if the bag is empty
    bag = request.session.get('bag', {})
    if not bag:
        # If the bag is empty, redirect to products page with a message
        messages.error(request, "There is nothing in your bag at the moment")
        return redirect(reverse('products'))
    
    current_bag = bag_contents(request)
    total = current_bag['grand_total']
    stripe_total = round(total * 100)
    # Initialize Stripe with the secret key
    stripe.api_key = stripe_secret_key
    # Create a payment intent with the total amount
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )
    # If the bag is not empty, create an order form
    order_form = OrderForm()
    template = 'checkout/checkout.html'
    # Check if the Stripe public key is set
    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    # Render the checkout template with the order form
    return render(request, template, context)
