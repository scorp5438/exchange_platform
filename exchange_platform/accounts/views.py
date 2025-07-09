from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('ads:index')

    def form_valid(self, form):
        response = super().form_valid(form)  # Сначала сохраняем форму
        user = form.save()
        login(self.request, user)  # Затем логиним
        return response

class MyLogoutView(LogoutView):
    next_page = reverse_lazy('ads:index')