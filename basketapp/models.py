from django.db import models
from django.conf import settings
from django.utils.functional import cached_property

from mainapp.models import Product


class BasketQuerySet(models.QuerySet):

   def delete(self, *args, **kwargs):
       for item in self:
           item.product.quantity += item.quantity
           item.product.save()
       super(BasketQuerySet, self).delete(*args, **kwargs)


class Basket(models.Model):
    objects = BasketQuerySet.as_manager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='basket')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='количество', default=0)
    add_datetime = models.DateTimeField(verbose_name='время', auto_now_add=True)

    @cached_property
    def get_items_cached(self):
        return self.user.basket.select_related()

    def get_total_quantity(self):
        _items = self.get_items_cached
        return sum(list(map(lambda x: x.quantity, _items)))

    def get_total_cost(self):
        _items = self.get_items_cached
        return sum(list(map(lambda x: x.product_cost, _items)))

    @property
    def product_cost(self):
        "return cost of all products this type"
        return self.product.price * self.quantity

    # @property
    # def total_quantity(self):
    #     "return total quantity for user"
    #     _items = Basket.objects.filter(user=self.user)
    #     _totalquantity = sum(list(map(lambda x: x.quantity, _items)))
    #     return _totalquantity
    #
    # @property
    # def total_cost(self):
    #     "return total cost for user"
    #     _items = Basket.objects.filter(user=self.user)
    #     _totalcost = sum(list(map(lambda x: x.product_cost, _items)))
    #     return _totalcost

    # def delete(self):
    #     self.product.quantity += self.quantity
    #     self.product.save()
    #     super(self.__class__, self).delete()
