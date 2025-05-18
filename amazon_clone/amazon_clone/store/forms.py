# Store App Forms (store/forms.py)
from django import forms
from .models import Review, CartItem, Product

class ReviewForm(forms.ModelForm):
    """Form for users to leave product reviews"""
    
    class Meta:
        model = Review
        fields = ['title', 'content', 'rating']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Review Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your review here', 'rows': 4}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }


class CartAddProductForm(forms.Form):
    """Form for adding products to cart with quantity"""
    
    quantity = forms.IntegerField(
        min_value=1,
        max_value=9,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class ProductSearchForm(forms.Form):
    """Form for searching products"""
    
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search Amazon'})
    )
    category = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Price'})
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Price'})
    )
    rating = forms.ChoiceField(
        required=False,
        choices=[(0, 'Any'), (4, '4+ stars'), (3, '3+ stars'), (2, '2+ stars'), (1, '1+ star')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('featured', 'Featured'),
            ('price_low', 'Price: Low to High'),
            ('price_high', 'Price: High to Low'),
            ('rating', 'Avg. Customer Review'),
            ('newest', 'Newest Arrivals')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super(ProductSearchForm, self).__init__(*args, **kwargs)
        # Dynamically populate category choices from database
        from .models import Category
        categories = Category.objects.all()
        self.fields['category'].choices = [('', 'All Categories')] + [(c.slug, c.name) for c in categories]