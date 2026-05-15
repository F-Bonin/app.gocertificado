from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages

class RoleRequiredMixin(AccessMixin):
    """Protege Views validando os booleanos do UserProfile."""
    required_role = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
            
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return self.handle_no_permission()

        if profile.is_company_admin:
            return super().dispatch(request, *args, **kwargs)

        if self.required_role and hasattr(profile, self.required_role):
            if getattr(profile, self.required_role) is False:
                messages.error(request, "Acesso Negado: Seu usuário não possui permissão para esta funcionalidade.")
                return redirect('certificates:dashboard')

        return super().dispatch(request, *args, **kwargs)
