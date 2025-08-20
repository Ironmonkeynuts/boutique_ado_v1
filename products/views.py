from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower

from .models import Product, Category
from .forms import ProductForm

# Create your views here.


def all_products(request):
    """ A view to show all products, including sorting and search queries """
    # Get all products
    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    # Check for GET parameters
    if request.GET:
        # Get the current sorting
        if 'sort' in request.GET:
            # Get the sort key from the GET parameters
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))

            if sortkey == 'category':
                sortkey = 'category__name'

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        # Get the current categories
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        # Check for search queries
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(
                    request,
                    "You didn't enter any search criteria!"
                )
                return redirect(reverse('products'))
            # Create a search query
            queries = Q(name__icontains=query) | Q(
                description__icontains=query)
            # Combine the search queries
            products = products.filter(queries)
    # Get the current sorting
    current_sorting = f'{sort}_{direction}'
    # Create a context dictionary to pass data to the template
    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }
    #
    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """
    # Get the product object
    product = get_object_or_404(Product, pk=product_id)
    # Check if the product exists
    context = {
        'product': product,
    }
    # Render the product detail template
    return render(request, 'products/product_detail.html', context)


def add_product(request):
    """ Add a product to the store """
    # Check if the request is a POST request
    if request.method == 'POST':
        # Bind the form to the request data
        form = ProductForm(request.POST, request.FILES)
        # Check if the form is valid
        if form.is_valid():
            # Save the form
            product = form.save()
            # Show a success message
            messages.success(request, 'Successfully added product!')
            # Redirect to the product detail page
            return redirect(reverse('product_detail', args=[product.id]))
        # If the form is not valid
        else:
            # Show an error message
            messages.error(
                request,
                'Failed to add product. Please ensure the form is valid.'
            )
    # If the request is not a POST request
    else:
        # Create a new form instance
        form = ProductForm()

    # Render the add product template
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    # Render the template with the context
    return render(request, template, context)


def edit_product(request, product_id):
    """ Edit a product in the store """
    # Get the product object
    product = get_object_or_404(Product, pk=product_id)
    # Check if the request is a POST request
    if request.method == 'POST':
        # Bind the form to the request data
        form = ProductForm(request.POST, request.FILES, instance=product)
        # Check if the form is valid
        if form.is_valid():
            # Save the form
            form.save()
            # Show a success message
            messages.success(request, 'Successfully updated product!')
            # Redirect to the product detail page
            return redirect(reverse('product_detail', args=[product.id]))
        # If the form is not valid
        else:
            # Show an error message
            messages.error(
                request,
                'Failed to update product. Please ensure the form is valid.'
            )
    else:
        # Bind the form to the product instance
        form = ProductForm(instance=product)
        # Show an info message
        messages.info(request, f'You are editing {product.name}')

    # Render the edit product template
    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    # Render the template with the context
    return render(request, template, context)


def delete_product(request, product_id):
    """ Delete a product from the store """
    # Get the product object
    product = get_object_or_404(Product, pk=product_id)
    # Delete the product
    product.delete()
    # Show a success message
    messages.success(request, 'Product deleted!')
    # Redirect to the products page
    return redirect(reverse('products'))
