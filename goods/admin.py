from django.contrib import admin
from .models import *

class shangpinAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock', 'category', 'brand', 'sales')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'caption')
    readonly_fields = ('create_time', 'update_time')

# 重新注册（覆盖默认）
admin.site.register(shangpin, shangpinAdmin)
admin.site.register(GoodsCategory)
admin.site.register(Brand)
admin.site.register(Guige)
admin.site.register(Guige_leixing)
admin.site.register(GoodsDetailImage)
admin.site.register(CartInfos)
admin.site.register(OrderInfos)
admin.site.register(Address)
admin.site.register(ProductReview)
admin.site.register(Favorite)   # 新增收藏模型