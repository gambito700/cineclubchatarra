from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2', 'rol']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuaria/o'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Repite la contraseña'
        self.fields['rol'].label = 'Tipo de cuenta'
        self.fields['rol'].choices = [('aficionado', 'Aficionade — quiero ver el feed y votar en encuestas'),
                                       ('patrocinador', 'Patrocinador — soy sponsor del cine club')]
