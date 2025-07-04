from django.contrib import admin
from .models import FoodItem, Order,Cart

admin.site.register(FoodItem)
admin.site.register(Cart)
admin.site.register(Order)