from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from .forms import CustomUserCreationForm, UbicacionForm
from .models import Ubicacion, CustomUser

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class UbicacionIndex(generic.ListView):
    template_name = 'users/ubicacionindex.html'
    context_object_name = 'ubicaciones'

    def get_queryset(self):
        return Ubicacion.objects.filter(user_id=self.kwargs['pk'])

def newubicacion(request, pk):
    if request.method == "POST":
        form = UbicacionForm(request.POST)
        if form.is_valid():
            request.user.ubicacion.delete()
            post = form.save(commit=False)
            post.user = request.user
            post.save()
    else:
        form = UbicacionForm()
    return render(request, 'users/newubicacion.html', {'form': form})

    

