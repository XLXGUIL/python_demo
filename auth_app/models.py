
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# 扩展用户资料表，和内置User一对一关联
class UserProfile(models.Model):
    # 关联内置User，用户删除时，资料也同步删除
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # 昵称（可选，最大20字）
    nickname = models.CharField(_('昵称'), max_length=20, blank=True, null=True)
    # 头像（上传到media/user_avatar目录，默认用默认头像）
    avatar = models.ImageField(
        _('头像'),
        upload_to='user_avatar/',
        default='user_avatar/default.png',  # 需自己创建该目录和默认图片
        blank=True,
        null=True
    )
    # 手机号（唯一，可选）
    phone = models.CharField(_('手机号'), max_length=11, blank=True, null=True, unique=True)
    # 性别（可选）
    GENDER_CHOICES = (
        (0, _('未知')),
        (1, _('男')),
        (2, _('女')),
    )
    gender = models.IntegerField(_('性别'), choices=GENDER_CHOICES, default=0)
    # 邮箱（可覆盖User默认邮箱，可选）
    email = models.EmailField(_('邮箱'), blank=True, null=True)
    # 资料更新时间
    updated_time = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('用户资料')
        verbose_name_plural = _('用户资料')

    def __str__(self):
        return f"{self.user.username}的资料"