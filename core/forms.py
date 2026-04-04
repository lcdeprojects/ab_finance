from django import forms
from .models import Payment, Cliente

class ClienteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common_class = "mt-1 block w-full rounded-md border-slate-200 dark:border-slate-700 dark:bg-slate-900 dark:text-white shadow-sm focus:border-primary focus:ring-primary focus:ring-1 sm:text-sm p-2 border transition-all outline-none"
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': common_class})

    class Meta:
        model = Cliente
        fields = ['nome', 'cpf', 'telefone']

class PaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common_class = "mt-1 block w-full rounded-md border-slate-200 dark:border-slate-700 dark:bg-slate-900 dark:text-white shadow-sm focus:border-primary focus:ring-primary focus:ring-1 sm:text-sm p-2 border transition-all outline-none"
        for name, field in self.fields.items():
            classes = common_class
            if name in ['total_value', 'down_payment']:
                classes += ' pl-9'
            field.widget.attrs.update({'class': classes})

    class Meta:
        model = Payment
        fields = ['cliente', 'total_value', 'down_payment', 'down_payment_is_paid', 'down_payment_date', 'installments', 'due_date', 'payment_method']
        widgets = {
            'down_payment_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'due_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'total_value': forms.NumberInput(attrs={'step': '0.01'}),
            'down_payment': forms.NumberInput(attrs={'step': '0.01'}),
        }
