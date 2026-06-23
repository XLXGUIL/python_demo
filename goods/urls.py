from django.urls import path
from . import views
app_name='goods'
urlpatterns=[
    path('index/', views.index, name='index'),
    path('category/<int:cid>/', views.index, name='category'),
    path('search/', views.search_goods, name='search'),  # 搜索路由
    path('detail/<int:id>',views.detail,name='detail'),
    path('addcart/<int:id>',views.addcart,name='addcart'),
    path('delt/<int:id>',views.delt,name='delt'),
    path('carts/', views.showcart, name='carts'),
    path('batch_delete/', views.batch_delete_cart, name='batch_delete'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirm_checkout/',views.confirm_checkout,name='confirm_checkout'),
    path('orderinfo/',views.showoderinfo,name='orderinfo'),
path('address/list/', views.address_list, name='address_list'),
path('address/add/', views.address_add, name='address_add'),
path('address/setdefault/<int:id>/', views.set_default, name='set_default'),
path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    # 新增功能路由
    path('address/delete/<int:id>/', views.address_delete, name='address_delete'),
    path('order/pay/<int:order_id>/', views.pay_order, name='pay_order'),
    path('order/confirm/<int:order_id>/', views.confirm_receipt, name='confirm_receipt'),
    path('favorite/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
]