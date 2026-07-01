from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from .forms import RegistroForm


class LoginPersonalizado(LoginView):
    template_name = 'accounts/login.html'

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos.')
        return super().form_invalid(form)


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, f'¡Bienvenide, {usuario.username}!')
            return redirect('core:feed')
    else:
        form = RegistroForm()
    return render(request, 'accounts/registro.html', {'form': form})
