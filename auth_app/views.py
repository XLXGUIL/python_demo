from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth import authenticate, login, logout
import re  # 用于正则校验手机号/邮箱/密码

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required  # 登录拦截装饰器
from django.contrib import messages  # 提示信息（比如修改成功）
from .models import UserProfile  # 方式1
from .models import User  # 方式2（自定义User）
from .forms import ProfileForm
from django.contrib.auth.models import User  # 方式1（内置User）

# 个人资料页面（查看+修改），登录后才能访问
@login_required(login_url='/auth/login/')  # 未登录跳转到登录页
def profile_view(request):
    # 方式1（扩展UserProfile）：获取当前用户的资料，没有则自动创建
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    # 方式2（自定义User）：直接获取当前用户
    # profile = request.user

    if request.method == 'POST':
        # 提交表单，绑定数据（request.FILES必须加，否则无法接收头像文件）
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # 可选：如果修改了邮箱，同步更新User模型的邮箱（方式1需要，方式2不需要）
            if form.cleaned_data.get('email'):
                request.user.email = form.cleaned_data['email']
                request.user.save()
            # 提示修改成功
            messages.success(request, '个人资料修改成功！')
            return redirect('auth_app:profile')  # 重定向到个人资料页，避免重复提交
    else:
        #  GET请求，展示当前用户的资料
        # 方式1：初始化表单，显示现有资料
        form = ProfileForm(instance=profile)
        # 方式2（自定义User）：form = ProfileForm(instance=request.user)

    # 传递表单和用户资料到模板
    context = {
        'form': form,
        'profile': profile,
        'user': request.user
    }
    return render(request, 'profile.html', context)
# 注册
class RegisterView(View):
    """此视图类用于响应http://127.0.0.1:8000/register的GET与POST请求"""

    def get(self, request):
        """处理GET请求"""
        state = request.GET.get('state', '')
        print('GET请求  state=', state)
        return render(request, 'register.html', {'state': state})

    def post(self, request):
        """处理POST请求"""
        # 1、接收请求参数
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        check_password = request.POST.get('check_password', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()

        # 2、校验请求参数（增强版）
        # 2.1 基础非空校验
        if not all([username, password, check_password, email, phone]):
            state = '所有字段均为必填项，请完整填写！'
            return render(request, 'register.html', {'state': state})

        # 2.2 用户名长度校验
        if len(username) < 3 or len(username) > 20:
            state = '用户名长度需在3-20位之间！'
            return render(request, 'register.html', {'state': state})

        # 2.3 密码一致性校验
        if password != check_password:
            state = '两次密码输入不一致，请重新输入！'
            return render(request, 'register.html', {'state': state})

        # 2.4 密码强度校验（字母+数字，至少8位）
        if len(password) < 8 or not re.match(r'^(?=.*[a-zA-Z])(?=.*\d).+$', password):
            state = '密码强度不足！需至少8位，包含字母和数字！'
            return render(request, 'register.html', {'state': state})

        # 2.5 手机号格式校验（11位数字，以1开头）
        if not re.match(r'^1[3-9]\d{9}$', phone):
            state = '手机号格式错误！请输入11位有效手机号！'
            return render(request, 'register.html', {'state': state})

        # 2.6 邮箱格式校验
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            state = '邮箱格式错误！请输入有效邮箱！'
            return render(request, 'register.html', {'state': state})

        # 2.7 用户名唯一性校验
        if User.objects.filter(username=username).exists():
            state = '该用户名已被注册，请更换用户名！'
            return render(request, 'register.html', {'state': state})

        # 2.8 邮箱唯一性校验
        if User.objects.filter(email=email).exists():
            state = '该邮箱已被注册，请更换邮箱！'
            return render(request, 'register.html', {'state': state})

        # 3、执行注册（保存数据）
        try:
            # 创建用户并关联邮箱（User模型默认支持email字段）
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            # 扩展：如果需要保存手机号，需自定义用户模型（此处先记录日志，后续可扩展）
            print(f"用户{username}注册成功，手机号：{phone}，邮箱：{email}")
            state = '注册成功！请前往登录页面登录！'
            # 注册成功后重定向到注册页（也可改为重定向到登录页）
            return redirect(reverse('auth_app:login') + f'?state={state}')

        except Exception as e:
            # 异常捕获，避免注册过程中报错
            print(f"注册失败：{str(e)}")
            state = '注册失败！服务器异常，请稍后重试！'
            return render(request, 'register.html', {'state': state})

# 登录视图（完善版）
class LoginView(View):
    """用户名登录（完整功能）"""

    def get(self, request):
        """处理登录页面GET请求：显示登录页，接收注册跳转的提示"""
        state = request.GET.get('state', '')  # 接收注册成功的提示
        return render(request, 'login.html', {'state': state})

    def post(self, request):
        """处理登录POST请求：校验账号密码、状态保持、记住我"""
        # 1. 接收前端参数
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        remembered = request.POST.get('remembered')  # 记住我复选框（on/None）

        # 2. 校验参数（非空、格式）
        if not username or not password:
            return render(request, 'login.html', {
                'account_errmsg': '用户名和密码不能为空！'
            })

        # 3. 认证用户（Django内置auth认证）
        user = authenticate(request, username=username, password=password)
        if user is None:
            # 账号或密码错误
            return render(request, 'login.html', {
                'account_errmsg': '用户名或密码错误，请重新输入！'
            })

        # 4. 实现状态保持（登录）
        login(request, user)

        # 5. 设置状态保持周期（记住我功能）
        if remembered == 'on':
            # 记住我：会话有效期2周（Django默认）
            request.session.set_expiry(60 * 60 * 24 * 14)
        else:
            # 不记住：浏览器关闭即失效
            request.session.set_expiry(0)

        # 6. 登录成功处理：跳转首页 + 写入用户名到Cookie
        response = redirect(reverse('goods:index'))
        # Cookie有效期15天，方便前端显示用户名
        response.set_cookie('username', user.username, max_age=60 * 60 * 24 * 15)

        return response
# 退出登录视图
class LogoutView(View):
    """用户退出登录（清空状态+删除Cookie）"""
    def get(self, request):
        # 清除Django的登录状态
        logout(request)
        # 跳转回登录页
        response = redirect(reverse('auth_app:login'))
        # 删除前端显示用户名的Cookie
        response.delete_cookie('username')
        return response

    class LoginView(View):
        def get(self, request):
            return render(request, "login.html")

        """用户名登录"""

        def post(self, request):
            username = request.POST['username']  # 用户名
            password = request.POST['password']  # 密码
            remembered = request.POST.get('remembered')  # 记住我复选框（on/None）
            role = request.POST.get('role', 'user')
            # 2. 校验参数（非空、格式）
            if not username or not password:
                return render(request, 'login.html', {
                    'account_errmsg': '用户名和密码不能为空！'
                })
            user = authenticate(username=username, password=password)
            # 5. 设置状态保持周期（记住我功能）
            if remembered == 'on':
                # 记住我：会话有效期2周（Django默认）
                request.session.set_expiry(60 * 60 * 24 * 14)
            else:
                # 不记住：浏览器关闭即失效
                request.session.set_expiry(0)
            if user is not None:
                login(request, user)  # 用户登录
                # return redirect(reverse('goods:index'))
                if role == 'admin':
                    response = redirect('/admin/')  # 管理员→后台
                else:
                    response = redirect(reverse('goods:index'))  # 用户→商城首页
                response.set_cookie('userid', user.id, max_age=60 * 90)
                return response
            else:
                return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})
