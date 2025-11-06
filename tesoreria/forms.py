from django import forms
from .models import Pago
from catalogos.models import Tercero, MetodoPago
from datetime import date


class CobroForm(forms.ModelForm):
    """
    Formulario para registrar cobros a clientes.
    """
    
    class Meta:
        model = Pago
        fields = [
            'tercero',
            'fecha_pago',
            'metodo_pago',
            'valor',
            'referencia',
            'observaciones',
        ]
        widgets = {
            'tercero': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'fecha_pago': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'metodo_pago': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de cheque, referencia de transferencia, etc.'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales (opcional)'
            }),
        }
        labels = {
            'tercero': 'Cliente',
            'fecha_pago': 'Fecha del Cobro',
            'metodo_pago': 'Método de Pago',
            'valor': 'Valor del Cobro',
            'referencia': 'Referencia',
            'observaciones': 'Observaciones',
        }
    
    def __init__(self, *args, **kwargs):
        self.empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar solo clientes de la empresa activa
        if self.empresa:
            self.fields['tercero'].queryset = Tercero.objects.filter(
                empresa=self.empresa,
                tipo_tercero__in=['cliente', 'ambos'],
                activo=True
            ).order_by('razon_social')
            
            self.fields['metodo_pago'].queryset = MetodoPago.objects.filter(
                empresa=self.empresa,
                activo=True
            ).order_by('nombre')
        
        # Establecer fecha por defecto
        if not self.instance.pk:
            self.initial['fecha_pago'] = date.today()
    
    def clean(self):
        cleaned_data = super().clean()
        tercero = cleaned_data.get('tercero')
        metodo_pago = cleaned_data.get('metodo_pago')
        referencia = cleaned_data.get('referencia')
        
        # Validar que el tercero sea cliente
        if tercero and not tercero.es_cliente:
            raise forms.ValidationError({
                'tercero': 'Debe seleccionar un cliente para registrar un cobro.'
            })
        
        # Validar referencia si el método la requiere
        if metodo_pago and metodo_pago.requiere_referencia and not referencia:
            raise forms.ValidationError({
                'referencia': f'El método de pago "{metodo_pago.nombre}" requiere una referencia.'
            })
        
        return cleaned_data
