from django.forms import BaseModelForm
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse_lazy
from LesProduits.models import *

from django.contrib.auth import *
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User

from LesProduits.forms import *
from django.core.mail import send_mail
from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.shortcuts import render

# def home(request):
#     return HttpResponse("Bienvenue sur l'accueil")

# def hello(request, name = ""):
#     return HttpResponse("<h1>Bonjour " + name + " content de vous revoir ici !</h1>")

# def list_products(request):
#     produits = Product.objects.all()
#     reponse = "<h1>Mes produits</h1> <ul>"
#     for produit in produits:
#         reponse += "<li>" + produit.name + " au prix de " + produit.price_ht.__str__() + "€</li>"
#     reponse += "</ul>"
#     return HttpResponse(reponse)

@login_required(login_url='/LesProduits/login/')
def home(request):
    return render(request, 'LesProduits/home.html')

def about(request):
    return render(request, 'LesProduits/about.html')

def contact(request):
    return render(request, 'LesProduits/contact.html')

def accueil(request,param):
    return HttpResponse("<h1>Hello " + param + " ! You're connected</h1>")

def listeProduits(request):
    prdcts = Product.objects.all()
    return render(request, 'LesProduits/list_products.html', {'prdcts': prdcts})

def listeDeclinaisons(request):
    declinaisons = ProductItem.objects.all()
    return render(request, 'LesProduits/list_items.html', {'liste_declinaisons': declinaisons})

# def detailProduit(request,id_produit):
#     # gérer cas d'erreur
#     produitRecherche = Product.objects.all().filter(code=id_produit)
#     print(produitRecherche)
#     return render(request, 'LesProduits/detail_product.html', {'produit': produitRecherche})


from django.views.generic import *

# class HomeView(TemplateView):
#     template_name = "LesProduits/home3.html"
#     def post(self, request, **kwargs):
#         return render(request, self.template_name)

class AboutView(TemplateView):
    template_name = "LesProduits/about.html"
    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        context['titreh1'] = "About us..."
        return context
    def post(self, request, **kwargs):
        return render(request, self.template_name)

@method_decorator(login_required(login_url='/LesProduits/login/'), name='dispatch')
class ProductListView(ListView):
    model = Product
    template_name = "LesProduits/list_products.html"
    context_object_name = "prdcts"

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['titremenu'] = "Liste des produits"
        return context

    def get_queryset(self):
        # Surcouche pour filtrer les résultats en fonction de la recherche
        # Récupérer le terme de recherche depuis la requête GET
        query = self.request.GET.get('search')
        print(query)
        if query:
            # Filtre les produits par nom (insensible à la casse)
            return Product.objects.filter(name__icontains=query)
        # Si aucun terme de recherche, retourner tous les produits
        return Product.objects.all()

class ProductDetailView(DetailView):
    model = Product
    template_name = "LesProduits/detail_product.html"
    context_object_name = "product"
    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['titremenu'] = "Détail produit"
        return context

class ProductAttributeListView(ListView):
    model = ProductAttribute
    template_name = "LesProduits/list_attributes.html"
    context_object_name = "productattributes"

    def get_queryset(self ):
        return ProductAttribute.objects.all().prefetch_related('productattributevalue_set')
    
    def get_context_data(self, **kwargs):
        context = super(ProductAttributeListView, self).get_context_data(**kwargs)
        context['titremenu'] = "Liste des attributs"
        return context
    
class ProductAttributeDetailView(DetailView):
    model = ProductAttribute
    template_name = "LesProduits/detail_attribute.html"
    context_object_name = "productattribute"

    def get_context_data(self, **kwargs):
        context = super(ProductAttributeDetailView, self).get_context_data(**kwargs)
        context['titremenu'] = "Détail attribut"
        context['values']=ProductAttributeValue.objects.filter(product_attribute=self.object).order_by('position')
        return context

class ProductItemListView(ListView):
    model = ProductItem
    template_name = "LesProduits/list_items.html"
    context_object_name = "productitems"

    def get_queryset(self ):
        return ProductItem.objects.select_related('product').prefetch_related('attributes')
    
    def get_context_data(self, **kwargs):
        context = super(ProductItemListView, self).get_context_data(**kwargs)
        context['titremenu'] = "Liste des déclinaisons"
        return context

class ProductItemDetailView(DetailView):
    model = ProductItem
    template_name = "LesProduits/detail_item.html"
    context_object_name = "productitem"

    def get_context_data(self, **kwargs):
        context = super(ProductItemDetailView, self).get_context_data(**kwargs)
        context['titremenu'] = "Détail déclinaison"
        # Récupérer les attributs associés à cette déclinaison
        context['attributes'] = self.object.attributes.all()
        return context

##################### Attribute (formulaire) #####################

class ProductAttributeUpdateView(UpdateView):
    model = ProductAttribute
    form_class = ProductAttributeForm
    template_name = "LesProduits/update_attribute.html"

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        attribute = form.save()
        return redirect('attribute-detail', attribute.id)

class ProductAttributeDeleteView(DeleteView):
    model = ProductAttribute
    template_name = "LesProduits/delete_attribute.html"
    success_url = reverse_lazy('attribute-list')

##################### Items (formulaire) #####################

class ProductItemUpdateView(UpdateView):
    model = ProductItem
    form_class = ProductItemForm
    template_name = "LesProduits/update_item.html"

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        item = form.save()
        return redirect('item-detail', item.id)

class ProductItemDeleteView(DeleteView):
    model = ProductItem
    template_name = "LesProduits/delete_item.html"
    success_url = reverse_lazy('item-list')

##################### Product (formulaire) #####################

# def ProductCreate(request):
#     if request.method == 'POST':
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             product = form.save()
#             return redirect('product-detail', product.id)
#     else:
#         form = ProductForm()
#     return render(request, "LesProduits/new_product.html", {'form': form})

class ProductCreateView(CreateView):
    model = Product
    form_class=ProductForm
    template_name = "LesProduits/new_product.html"

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        product = form.save()
        return redirect('product-detail', product.id)
    
class ProductUpdateView(UpdateView):
    model = Product
    form_class=ProductForm
    template_name = "LesProduits/update_product.html"

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        product = form.save()
        return redirect('product-detail', product.id)

class ProductDeleteView(DeleteView):
    model = Product
    template_name = "LesProduits/delete_product.html"
    success_url = reverse_lazy('product-list')

##################### Contact us (formulaire) #####################

def ContactView(request):
    if request.method=='POST':
        form = ContactUsForm(request.POST)
        form = ContactUsForm(request.POST)
        if form.is_valid():
            send_mail(
            subject= "Message from " + form.cleaned_data["name"] or "anonyme" + "via MonProjet Contact Us form",
            message=form.cleaned_data['message'],
            from_email=form.cleaned_data['email'],
            recipient_list=['marin.tremine@gmail.com'],
            )
            return redirect('email_sent')
    else:
        form = ContactUsForm()
    titreh1 = "Contact us !"
    print('La méthode de requête est : ', request.method)
    print('Les données POST sont : ', request.POST)
    return render(request, "LesProduits/contact.html",{'titreh1':titreh1, 'form':form})

##################### Connexion / Inscription #####################

class ConnectView(LoginView):
    template_name = 'LesProduits/login.html'
    def post(self, request, **kwargs):
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return render(request, 'LesProduits/home.html',{'titreh1':username})
        else:
            return render(request, 'LesProduits/login.html', {'erreurConnexion' : "Username ou password incorrect."})

class RegisterView(TemplateView):
    template_name = 'LesProduits/register.html'
    def post(self, request, **kwargs):
        username = request.POST.get('username', False)
        mail = request.POST.get('mail', False)
        password = request.POST.get('password', False)
        user = User.objects.create_user(username, mail, password)
        user.save()
        if user is not None and user.is_active:
            return render(request, 'LesProduits/login.html')
        else:
            return render(request, 'LesProduits/register.html')

class DisconnectView(TemplateView):
    template_name = 'LesProduits/logout.html'
    def get(self, request, **kwargs):
        logout(request)
        return render(request, self.template_name)