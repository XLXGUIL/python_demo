from django.db import models
from django.db import models
from django.contrib.auth.models import User

class Guige_leixing(models.Model):
    # 服饰     白色，黑色
    # 电子产品    128g 256g
    name = models.CharField(max_length=100, verbose_name='规格类型')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = '商品规格类型'
        verbose_name_plural = verbose_name
#Guige
class Guige(models.Model):
    name = models.CharField(max_length=100, verbose_name='规格')
    guige_leixing = models.ForeignKey(Guige_leixing, verbose_name='规格类型id', null=True, on_delete=models.PROTECT)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = '商品规格'
        verbose_name_plural = verbose_name

class GoodsCategory(models.Model):
    """商品类别"""
    name = models.CharField(max_length=10, verbose_name='名称')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'tb_goods_category'
        verbose_name = '商品类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Brand(models.Model):
    """品牌"""
    name = models.CharField(max_length=20, verbose_name='名称')
    logo = models.ImageField(verbose_name='Logo图片', upload_to='images')
    first_letter = models.CharField(max_length=1, verbose_name='品牌首字母')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = 'tb_brand'
        verbose_name = '品牌'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class shangpin(models.Model):
    """商品"""
    name = models.CharField(max_length=50, verbose_name='名称')
    caption = models.CharField(max_length=100, verbose_name='副标题')
    # ForeignKey  一对多关系，一个商品可对应多个可选类别
    category = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, verbose_name='从属类别')
    # 一个商品可对应多个可选品牌
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name='品牌')
    guige_leixing = models.ForeignKey(Guige_leixing, on_delete=models.PROTECT, verbose_name='规格类型',null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')  # decimal_places 存储十进位数
    stock = models.IntegerField(default=0, verbose_name='库存')
    sales = models.IntegerField(default=0, verbose_name='销量')
    comments = models.IntegerField(default=0, verbose_name='评价数')

    # upload_to = 'images' 指定相对路径
    image = models.ImageField(max_length=200, verbose_name='展示图片', upload_to='images')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")



    class Meta:
        db_table = 'tb_shangpin'
        verbose_name = '商品信息'
        verbose_name_plural = verbose_name

    # 原有模型保持不变，新增以下模型


    def __str__(self):
        return '%s: %s' % (self.id, self.name)
# 原有模型保持不变，新增以下模型
class GoodsDetailImage(models.Model):
    """商品详情图片"""
    shangpin = models.ForeignKey(
        'shangpin',
        on_delete=models.CASCADE,
        verbose_name='关联商品',
        related_name='detail_images'  # 反向关联名称，用于模板取值
    )
    image = models.ImageField(
        upload_to='detail_images/',  # 详情图片存储路径（media/detail_images/）
        verbose_name='详情图片'
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    sort = models.IntegerField(default=0, verbose_name='排序（数字越小越靠前）')

    class Meta:
        db_table = 'tb_goods_detail_image'
        verbose_name = '商品详情图片'
        verbose_name_plural = verbose_name
        ordering = ['sort']  # 按排序字段升序排列

    def __str__(self):
        return f"{self.shangpin.name} - 详情图{self.id}"

class CartInfos(models.Model):
    num = models.IntegerField(verbose_name='购买数量')
    user_id = models.IntegerField('用户ID')
    shangpin_id = models.IntegerField('商品ID')
    guige_id = models.IntegerField('规格ID', null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", null=True)
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = '购物车'
        db_table = 'tb_cartinfo'
STATE = (
    ('待支付', '待支付'),
    ('已支付', '已支付'),
    ('发货中', '发货中'),
    ('已签收', '已签收'),
    ('退货中', '退货中'),
)
class OrderInfos(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.FloatField('订单总价')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", null=True)
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", null=True)
    user_id = models.IntegerField('用户ID')
    state = models.CharField('订单状态', max_length=20, choices=STATE)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = '订单信息'
        verbose_name_plural = '订单信息'
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="用户")
    receiver = models.CharField(max_length=20, verbose_name="收货人")
    phone = models.CharField(max_length=11, verbose_name="手机号")
    province = models.CharField(max_length=20, verbose_name="省份")
    city = models.CharField(max_length=20, verbose_name="城市")
    district = models.CharField(max_length=20, verbose_name="区县")
    detail = models.CharField(max_length=200, verbose_name="详细地址")
    is_default = models.BooleanField(default=False, verbose_name="是否默认")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return f"{self.receiver} {self.phone} {self.province}{self.city}{self.district}{self.detail}"

    class Meta:
        verbose_name = "收货地址"
        verbose_name_plural = "收货地址"
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

# 获取用户模型
User = get_user_model()

# 商品评价模型（新增）
class ProductReview(models.Model):
    # 评分选项（1-5星）
    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评价用户')
    product = models.ForeignKey('shangpin', on_delete=models.CASCADE, verbose_name='评价商品')
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='评分'
    )
    content = models.TextField(max_length=500, verbose_name='评价内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_anonymous = models.BooleanField(default=False, verbose_name='匿名评价')

    class Meta:
        verbose_name = '商品评价'
        verbose_name_plural = '商品评价'
        ordering = ['-created_at']  # 按创建时间倒序
        unique_together = ['user', 'product']  # 每个用户对同一商品只能评价一次

    def __str__(self):
        return f"{self.user.username}对{self.product.name}的评价"

    def get_rating_display(self):
        """返回评分的星级展示文本"""
        return dict(self.RATING_CHOICES).get(self.rating, '')
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    product = models.ForeignKey('shangpin', on_delete=models.CASCADE, verbose_name='商品')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = '收藏'
        verbose_name_plural = '收藏'

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.product.name}"