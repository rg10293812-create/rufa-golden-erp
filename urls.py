from django import forms
from django.contrib.auth.models import User
from .models import Deal, ExternalMarketer, FinancialTransaction, Property, PropertyImage, Task, UserProfile


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'property_type', 'district', 'price', 'area', 'specifications', 'notes', 'owner_name', 'owner_phone', 'status']
        widgets = {f: forms.TextInput(attrs={'class': 'form-control'}) for f in ['title','property_type','district','area','owner_name','owner_phone']}
        widgets.update({
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'specifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        })


class MultiImageForm(forms.Form):
    images = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'related_property']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'related_property': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'username')
        self.fields['related_property'].required = False


class TaskCompleteForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['result_notes', 'attachment']
        widgets = {
            'result_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }


class FinancialTransactionForm(forms.ModelForm):
    class Meta:
        model = FinancialTransaction
        fields = ['transaction_type', 'title', 'amount', 'category', 'date', 'notes']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = ['property', 'title', 'commission_amount', 'company_percentage', 'external_marketer', 'status']
        widgets = {
            'property': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'commission_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'company_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'external_marketer': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class ExternalMarketerForm(forms.ModelForm):
    class Meta:
        model = ExternalMarketer
        fields = ['name', 'phone', 'company', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class UserCreateForm(forms.Form):
    username = forms.CharField(label='اسم المستخدم', widget=forms.TextInput(attrs={'class': 'form-control'}))
    full_name = forms.CharField(label='الاسم', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='كلمة المرور', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(label='الدور', choices=UserProfile.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    phone = forms.CharField(label='الجوال', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
