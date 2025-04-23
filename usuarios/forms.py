# usuarios/forms.py
from django import forms
from .models import Habitacion
from .models import Reserva
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
#from django.utils import timezone
from datetime import date 

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ["username", "email"]
    
    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not password or len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class BuscarHabitacionForm(forms.Form):
    numero = forms.IntegerField(required=False, label="Número de habitación")
    tipo = forms.CharField(required=False, label="Tipo de habitación")
    capacidad = forms.IntegerField(required=False, label="Capacidad mínima")
    precio_por_noche = forms.DecimalField(
        required=False,
        label="Precio máximo por noche",
        max_digits=8,
        decimal_places=2
    )
    disponibilidad = forms.ChoiceField(
        required=False,
        choices=[('', '---------'), ('True', 'Disponible'), ('False', 'No disponible')],
        label="Disponibilidad"
    )

class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitacion
        fields = ['numero', 'tipo', 'capacidad', 'precio_por_noche', 'disponible']



class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha_inicio', 'fecha_fin', 'habitacion']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_fecha_inicio(self):
        fecha_inicio = self.cleaned_data.get('fecha_inicio')

        # Verificar si la fecha de inicio es anterior a la fecha actual
        if fecha_inicio is None:
            raise ValidationError("La fecha de inicio no puede estar vacía.")
        if fecha_inicio < date.today():
            raise ValidationError("La fecha de inicio no puede ser anterior a la fecha actual.")
        return fecha_inicio

    def clean_fecha_fin(self):
        fecha_fin = self.cleaned_data.get('fecha_fin')
        fecha_inicio = self.cleaned_data.get('fecha_inicio')

        # Verificar si la fecha de fin y la fecha de inicio son válidas
        if fecha_fin is None:
            raise ValidationError("La fecha de fin no puede estar vacía.")
        if fecha_inicio is None:
            raise ValidationError("La fecha de inicio no puede estar vacía.")

        # Verificar si la fecha de fin es antes de la fecha de inicio
        if fecha_fin <= fecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")
        return fecha_fin