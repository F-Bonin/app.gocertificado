from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Libera rotas de estáticos, logout e a própria tela de troca de senha
            if request.path in [reverse('accounts:change_password'), reverse('accounts:logout')] or request.path.startswith('/static/'):
                return self.get_response(request)

            profile = getattr(request.user, 'profile', None)
            if profile and getattr(profile, 'must_change_password', False):
                messages.warning(request, "Por motivos de segurança, você deve alterar sua senha provisória neste primeiro acesso.")
                return redirect('accounts:change_password')

        return self.get_response(request)
