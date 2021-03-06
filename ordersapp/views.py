from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.db import transaction

from django.forms import inlineformset_factory

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

from basketapp.models import Basket
from ordersapp.models import Order, OrderItem
from ordersapp.forms import OrderItemForm


class OrderList(ListView):
   model = Order

   def get_queryset(self):
       return Order.objects.filter(user=self.request.user)


class OrderCreateView(CreateView):
   model = Order
   fields = []
   success_url = reverse_lazy('ordersapp:orders_list')

   def get_context_data(self, **kwargs):
       data = super().get_context_data(**kwargs)
       OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1)

       if self.request.POST:
           formset = OrderFormSet(self.request.POST)
       else:
           basket_items = Basket.objects.filter(user=self.request.user)
           if len(basket_items):
               OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=len(basket_items))
               formset = OrderFormSet()
               for num, form in enumerate(formset.forms):
                   form.initial['product'] = basket_items[num].product
                   form.initial['quantity'] = basket_items[num].quantity
                   form.initial['price'] = basket_items[num].product.price
               basket_items.delete()
           else:
               formset = OrderFormSet()

       data['orderitems'] = formset
       return data

   def form_valid(self, form):
       context = self.get_context_data()
       orderitems = context['orderitems']

       with transaction.atomic():
           form.instance.user = self.request.user
           self.object = form.save()
           if orderitems.is_valid():
               orderitems.instance = self.object
               orderitems.save()

       # удаляем пустой заказ
       if self.object.get_total_cost() == 0:
           self.object.delete()

       return super().form_valid(form)


class OrderRead(DetailView):
   model = Order

   def get_context_data(self, **kwargs):
       context = super(OrderRead, self).get_context_data(**kwargs)
       context['title'] = 'заказ/просмотр'
       return context


class OrderDelete(DeleteView):
   model = Order
   success_url = reverse_lazy('ordersapp:orders_list')


class OrderUpdateView(UpdateView):
    model = Order
    fields = []
    success_url = reverse_lazy('ordersapp:orders_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1)

        if self.request.POST:
            formset = OrderFormSet(self.request.POST, instance=self.object)
        else:
            formset = OrderFormSet(instance=self.object)
            for form in formset.forms:
                if form.instance.pk:
                    form.initial['price'] = form.instance.product.price
            data['orderitems'] = formset

        data['orderitems'] = formset
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            self.object = form.save()
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()

        # удаляем пустой заказ
        if self.object.get_total_cost() == 0:
            self.object.delete()

        return super().form_valid(form)
