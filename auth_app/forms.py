from django import forms
from .models import UserProfile  # 方式1用这个
from .models import User  # 方式2用这个（自定义User模型）
from django.contrib.auth.models import User  # 方式1用这个（内置User）
import re

# 个人资料修改表单
class ProfileForm(forms.ModelForm):
    # 手机号验证（可选，添加正则校验）
    phone = forms.CharField(
        required=False,  # 可选字段，不填也可以
        widget=forms.TextInput(attrs={'placeholder': '请输入11位手机号'}),
        error_messages={'invalid': '请输入正确的11位手机号'}
    )

    class Meta:
        # 方式1（扩展UserProfile）：关联UserProfile模型
        model = UserProfile
        # 方式2（自定义User）：关联User模型，字段改为['nickname', 'avatar', 'phone', 'gender', 'email']
        fields = ['nickname', 'avatar', 'phone', 'gender', 'email']
        # 表单样式（和你登录/注册表单样式保持一致，可自行调整）
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入昵称（不超过20字）'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            # 头像上传控件，样式可自定义
            'avatar': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    # 手机号正则校验（自定义验证逻辑）
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:  # 如果用户填了手机号，才校验
            if not re.match(r'^1[3-9]\d{9}$', phone):
                raise forms.ValidationError('请输入正确的11位手机号')
        return phone

# 可选：如果想单独做头像上传表单（可忽略，上面的表单已包含头像）
class AvatarForm(forms.ModelForm):
    class Meta:
        model = UserProfile  # 方式1
        # model = User  # 方式2
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control-file'}),
        }