from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from django.views import generic
from paypal.standard.forms import PayPalPaymentsForm

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import CheckoutForm
from .models import ProdukItem, OrderProdukItem, Order, AlamatPengiriman, Payment

class HomeListView(generic.ListView):
    template_name = 'home.html'
    queryset = ProdukItem.objects.all()
    paginate_by = 4

class ContactView(generic.ListView):
    template_name = 'kontak.html'
    queryset = ProdukItem.objects.all()
    paginate_by = 4

class ProductListView(generic.ListView):
    template_name = 'list_produk.html'
    queryset = ProdukItem.objects.all()
    paginate_by = 4

class ProductDetailView(generic.DetailView):
    template_name = 'product_detail.html'
    queryset = ProdukItem.objects.all()

class CheckoutView(LoginRequiredMixin, generic.FormView):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order.produk_items.count() == 0:
                messages.warning(self.request, 'Belum ada belajaan yang Anda pesan, lanjutkan belanja')
                return redirect('toko:home-produk-list')
        except ObjectDoesNotExist:
            order = {}
            messages.warning(self.request, 'Belum ada belajaan yang Anda pesan, lanjutkan belanja')
            return redirect('toko:home-produk-list')

        context = {
            'form': form,
            'keranjang': order,
        }
        template_name = 'checkout.html'
        return render(self.request, template_name, context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                alamat_1 = form.cleaned_data.get('alamat_1')
                alamat_2 = form.cleaned_data.get('alamat_2')
                negara = form.cleaned_data.get('negara')
                kode_pos = form.cleaned_data.get('kode_pos')
                opsi_pembayaran = form.cleaned_data.get('opsi_pembayaran')
                alamat_pengiriman = AlamatPengiriman(
                    user=self.request.user,
                    alamat_1=alamat_1,
                    alamat_2=alamat_2,
                    negara=negara,
                    kode_pos=kode_pos,
                )

                alamat_pengiriman.save()
                order.alamat_pengiriman = alamat_pengiriman
                order.save()
                if opsi_pembayaran == 'P':
                    return redirect('toko:payment', payment_method='paypal')
                else:
                    return redirect('toko:payment', payment_method='stripe')

            messages.warning(self.request, 'Gagal checkout')
            return redirect('toko:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, 'Tidak ada pesanan yang aktif')
            return redirect('toko:order-summary')

class PaymentView(LoginRequiredMixin, generic.FormView):
    def get(self, *args, **kwargs):
        template_name = 'payment.html'
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            
            paypal_data = {
                'business': settings.PAYPAL_RECEIVER_EMAIL,
                'amount': order.get_total_harga_order,
                'item_name': f'Pembayaran belajanan order: {order.id}',
                'invoice': f'{order.id}-{timezone.now().timestamp()}' ,
                'currency_code': 'USD',
                'notify_url': self.request.build_absolute_uri(reverse('paypal-ipn')),
                'return_url': self.request.build_absolute_uri(reverse('toko:paypal-return')),
                'cancel_return': self.request.build_absolute_uri(reverse('toko:paypal-cancel')),
            }
        
            qPath = self.request.get_full_path()
            isPaypal = 'paypal' in qPath
        
            form = PayPalPaymentsForm(initial=paypal_data)
            context = {
                'paypalform': form,
                'order': order,
                'is_paypal': isPaypal,
            }
            return render(self.request, template_name, context)

        except ObjectDoesNotExist:
            return redirect('toko:checkout')

class OrderSummaryView(LoginRequiredMixin, generic.TemplateView):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'keranjang': order
            }
            template_name = 'order_summary.html'
            return render(self.request, template_name, context)
        except ObjectDoesNotExist:
            messages.error(self.request, 'Tidak ada pesanan yang aktif')
            return redirect('/')

def add_to_cart(request, slug):
    if request.user.is_authenticated:
        produk_item = get_object_or_404(ProdukItem, slug=slug)
        order_produk_item, _ = OrderProdukItem.objects.get_or_create(
            produk_item=produk_item,
            user=request.user,
            ordered=False
        )
        order_query = Order.objects.filter(user=request.user, ordered=False)
        if order_query.exists():
            order = order_query[0]
            if order.produk_items.filter(produk_item__slug=produk_item.slug).exists():
                order_produk_item.quantity += 1
                order_produk_item.save()
                pesan = f"ProdukItem sudah diupdate menjadi: { order_produk_item.quantity }"
                messages.info(request, pesan)
                return redirect('toko:produk-detail', slug = slug)
            else:
                order.produk_items.add(order_produk_item)
                messages.info(request, 'ProdukItem pilihanmu sudah ditambahkan')
                return redirect('toko:produk-detail', slug = slug)
        else:
            tanggal_order = timezone.now()
            order = Order.objects.create(user=request.user, tanggal_order=tanggal_order)
            order.produk_items.add(order_produk_item)
            messages.info(request, 'ProdukItem pilihanmu sudah ditambahkan')
            return redirect('toko:produk-detail', slug = slug)
    else:
        return redirect('/accounts/login')

def remove_from_cart(request, slug):
    if request.user.is_authenticated:
        produk_item = get_object_or_404(ProdukItem, slug=slug)
        order_query = Order.objects.filter(
            user=request.user, ordered=False
        )
        if order_query.exists():
            order = order_query[0]
            if order.produk_items.filter(produk_item__slug=produk_item.slug).exists():
                try: 
                    order_produk_item = OrderProdukItem.objects.filter(
                        produk_item=produk_item,
                        user=request.user,
                        ordered=False
                    )[0]
                    
                    order.produk_items.remove(order_produk_item)
                    order_produk_item.delete()

                    pesan = f"ProdukItem sudah dihapus"
                    messages.info(request, pesan)
                    return redirect('toko:produk-detail',slug = slug)
                except ObjectDoesNotExist:
                    print('Error: order ProdukItem sudah tidak ada')
            else:
                messages.info(request, 'ProdukItem tidak ada')
                return redirect('toko:produk-detail',slug = slug)
        else:
            messages.info(request, 'ProdukItem tidak ada order yang aktif')
            return redirect('toko:produk-detail',slug = slug)
    else:
        return redirect('/accounts/login')

# @csrf_exempt
def paypal_return(request):
    if request.user.is_authenticated:
        try:
            print('paypal return', request)
            order = Order.objects.get(user=request.user, ordered=False)
            payment = Payment()
            payment.user=request.user
            payment.amount = order.get_total_harga_order()
            payment.payment_option = 'P' # paypal kalai 'S' stripe
            payment.charge_id = f'{order.id}-{timezone.now()}'
            payment.timestamp = timezone.now()
            payment.save()
            
            order_produk_item = OrderProdukItem.objects.filter(user=request.user,ordered=False)
            order_produk_item.update(ordered=True)
            
            order.payment = payment
            order.ordered = True
            order.save()

            messages.info(request, 'Pembayaran sudah diterima, terima kasih')
            return redirect('toko:home-produk-list')
        except ObjectDoesNotExist:
            messages.error(request, 'Periksa kembali pesananmu')
            return redirect('toko:order-summary')
    else:
        return redirect('/accounts/login')

# @csrf_exempt
def paypal_cancel(request):
    messages.error(request, 'Pembayaran dibatalkan')
    return redirect('toko:order-summary')

def filter_products(request):
    filtered_products = None
    selected_kategori = request.GET.getlist('kategori')
    selected_tags = request.GET.getlist('tags')


    if selected_kategori or selected_tags:
        filtered_products = ProdukItem.objects.all()
        if selected_kategori:
            filtered_products = filtered_products.filter(kategori__in=selected_kategori)
        if selected_tags:
            filtered_products = filtered_products.filter(label__in=selected_tags)
    else:
        filtered_products = ProdukItem.objects.all()

    return render(request, 'home.html', {'object_list': filtered_products})
    
def pencarian_barang(request):
    keyword = request.GET.get('keyword')

    if keyword:
        barang = ProdukItem.objects.filter(nama_produk__icontains=keyword)
    else:
        barang = None
    
    return render(request, 'home.html', {'object_list': barang})

def update_quantity(request: HttpRequest):
    if request.method == 'POST' and request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        total = 0.0
        hemat = 0.0
        total_all = None
        total_hemat = None

        try:
            product = OrderProdukItem.objects.get(id=product_id)
            if action == 'increase':
                product.quantity += 1
            elif action == 'decrease':
                if product.quantity > 1:
                    product.quantity -= 1
            product.save()

            if product.produk_item.harga_diskon:
                total = product.get_total_harga_diskon_item()
                hemat = product.get_total_hemat_item()
            else :
                total = product.get_total_harga_item()
                
            return JsonResponse({'quantity': product.quantity, 'total':total, 'hemat':hemat})
        except OrderProdukItem.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def reduce_from_cart(request, slug):
    if request.user.is_authenticated:
        produk_item = get_object_or_404(ProdukItem, slug=slug)
        order_produk_item, _ = OrderProdukItem.objects.get_or_create(
            produk_item=produk_item,
            user=request.user,
            ordered=False
        )
        order_query = Order.objects.filter(user=request.user, ordered=False)
        if order_query.exists():
            order = order_query[0]
            if order.produk_items.filter(produk_item__slug=produk_item.slug).exists():
                if order_produk_item.quantity > 1 :
                    order_produk_item.quantity -= 1
                    order_produk_item.save()
                    pesan = f"ProdukItem sudah diupdate menjadi: { order_produk_item.quantity }"
                    messages.info(request, pesan)
                else:
                    pesan = f"Produk Item tidak bisa di update"
                    messages.warning(request, pesan)
                return redirect('toko:produk-detail', slug = slug)
            else:
                messages.info(request, 'ProdukItem pilihanmu tidak ada pada keranjang')
                return redirect('toko:produk-detail', slug = slug)
        else:
            messages.info(request, 'ProdukItem pilihanmu tidak ada pada keranjang')
            return redirect('toko:produk-detail', slug = slug)
    else:
        return redirect('/accounts/login')

def cari_produk(request, kategori):
    produk = ProdukItem.objects.filter(kategori=kategori)
    return render(request, 'home.html', {'object_list': produk})


# def update_cart(request, slug):
#     def get(self, *args, **kwargs):
#         if request.user.is_authenticated:
#             produk_item = get_object_or_404(ProdukItem, slug=slug)
#             order_produk_item, _ = OrderProdukItem.objects.get_or_create(
#                 produk_item=produk_item,
#                 user=request.user,
#                 ordered=False
#             )
#             order_query = Order.objects.filter(user=request.user, ordered=False)
#             if order_query.exists():
#                 order = order_query[0]
#                 if order.produk_items.filter(produk_item__slug=produk_item.slug).exists():
#                     order_produk_item.quantity += 1
#                     order_produk_item.save()

#                     order = Order.objects.get(user=self.request.user, ordered=False)
#                     context = {
#                         'keranjang': order
#                     }
#                     template_name = 'order_summary.html'
#                     return render(self.request, template_name, context)
#         else:
#             return redirect('/accounts/login')
