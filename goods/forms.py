from django import forms
from .models import ProductReview

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'content', 'is_anonymous']  # 需提交的字段
        widgets = {
            # 评价内容文本框样式
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': '请分享您对商品的真实体验...',
                'class': 'form-control'
            }),
            # 评分单选框样式
            'rating': forms.RadioSelect(attrs={
                'class': 'rating-radio'
            }),
            # 匿名评价复选框样式
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        # 自定义字段标签
        labels = {
            'content': '评价内容',
            'is_anonymous': '匿名评价'
        }