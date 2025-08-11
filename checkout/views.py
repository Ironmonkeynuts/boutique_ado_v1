from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.contexts import bag_contents

import stripe


def checkout(request):
    """ Checkout view to handle the checkout process. """
    # Get the Stripe public and secret keys from settings
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the bag from the session
        bag = request.session.get('bag', {})
        # Get the form data from the POST request
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # Create an order form instance
        order_form = OrderForm(form_data)
        # Check if the form is valid
        if order_form.is_valid():
            # If the form is valid, save the order
            order = order_form.save()
            for item_id, item_data in bag.items():
                try:
                    # Get the product from the database
                    product = Product.objects.get(id=item_id)
                    # Create an order line item for each product in the bag
                    # If item_data is an integer, product has no size
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    # If item_data is a dictionary, product has sizes
                    else:
                        # Iterate through the sizes and quantities
                        for size, quantity in item_data[
                                'items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                # If the product does not exist, show an error message
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your "
                        "bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    # Delete the order if it was created
                    order.delete()
                    # Redirect to the bag view
                    return redirect(reverse('view_bag'))
            # Save information about the order
            request.session['save_info'] = 'save-info' in request.POST
            # Redirect to the checkout success page with the order number
            return redirect(
                reverse('checkout_success', args=[order.order_number]))
        else:
            # If the form is not valid, show an error message
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')

    else:
        # Check if the bag is empty
        bag = request.session.get('bag', {})
        if not bag:
            # If the bag is empty, redirect to products page with a message
            messages.error(
                request, "There is nothing in your bag at the moment")
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
        # Check if the Stripe public key is set
        if not stripe_public_key:
            messages.warning(request, 'Stripe public key is missing. \
                Did you forget to set it in your environment?')
        template = 'checkout/checkout.html'
        context = {
            'order_form': order_form,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,
        }

        # Render the checkout template with the order form
        return render(request, template, context)


def checkout_success(request, order_number):
    """ Handle successful checkout and display order confirmation. """
    # Check user wants to save their information
    save_info = request.session.get('save_info')
    # Get the order details
    order = get_object_or_404(Order, order_number=order_number)
    # Order confirmation message with order number and email
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation email \
        will be sent to {order.email}.')
    # Delete user's bag from the session
    if 'bag' in request.session:
        del request.session['bag']
    # Render the checkout success template with order details
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }
    return render(request, template, context)
