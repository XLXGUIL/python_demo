from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime

from goods.models import (
    shangpin, GoodsCategory, Guige, GoodsDetailImage,
    CartInfos, OrderInfos, Address, ProductReview
)
from goods.forms import ReviewForm   # 注意 forms.py 中定义了 ReviewForm


@login_required
def index(request):
    cid = request.GET.get('cid', 0)
    categories = GoodsCategory.objects.all()
    if cid and cid.isdigit():
        shangpin_list = shangpin.objects.filter(category_id=cid)
    else:
        shangpin_list = shangpin.objects.all()
    return render(request, 'index.html', {
        'shangpin': shangpin_list,
        'categories': categories
    })


@login_required
def search_goods(request):
    keyword = request.GET.get('keyword', '')
    goods_list = []
    if keyword:
        goods_list = shangpin.objects.filter(
            Q(name__icontains=keyword) | Q(caption__icontains=keyword)
        )
    category_list = GoodsCategory.objects.all()
    return render(request, 'index.html', {
        'goods_list': goods_list,
        'category_list': category_list,
        'keyword': keyword,
    })

@login_required
def detail(request, id):
    shangpin1 = get_object_or_404(shangpin, id=id)
    guige = Guige.objects.filter(guige_leixing_id=shangpin1.guige_leixing_id)
    detail_images = GoodsDetailImage.objects.filter(shangpin=shangpin1)

    # 评价相关
    reviews = ProductReview.objects.filter(product=shangpin1).order_by('-created_at')
    review_count = reviews.count()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    user_has_reviewed = ProductReview.objects.filter(
        user=request.user,
        product=shangpin1
    ).exists()

    # 用户是否购买过该商品（用于控制“发表评价”按钮）
    user_has_purchased = False
    if shangpin1:
        paid_orders = OrderInfos.objects.filter(
            user_id=request.user.id,
            state__in=['待支付', '已支付', '已完成', '待发货', '已发货']
        )
        if paid_orders.exists():
            purchased_cart_items = CartInfos.objects.filter(
                user_id=request.user.id,
                shangpin_id=shangpin1.id,
            ).exists()
            user_has_purchased = purchased_cart_items

    return render(request, 'detail.html', {
        'shangpin': shangpin1,
        'guiges': guige,
        'detail_images': detail_images,
        'reviews': reviews[:10],
        'review_count': review_count,
        'average_rating': average_rating,
        'user_has_reviewed': user_has_reviewed,
        'user_has_purchased': user_has_purchased,
    })


@login_required
def showcart(request):
    userid = request.user.id
    carts = CartInfos.objects.filter(user_id=userid)
    sumlist = []
    for cart in carts:
        good = shangpin.objects.get(id=cart.shangpin_id)
        guige = Guige.objects.filter(id=cart.guige_id).first() if cart.guige_id else None
        guige_name = guige.name if guige else '随机'
        sumlist.append({
            'cart': cart,
            'good': good,
            'guige_name': guige_name
        })
    return render(request, 'cart.html', {'sumlist': sumlist})


@login_required
def addcart(request, id):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            guige_id = request.POST.get('guige_id')
            guige_id = int(guige_id) if guige_id and guige_id.isdigit() else None
            cart_item, created = CartInfos.objects.get_or_create(
                user_id=request.user.id,
                shangpin_id=id,
                guige_id=guige_id,
                defaults={'num': quantity}
            )
            if not created:
                cart_item.num += quantity
                cart_item.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': '添加成功'})
            return redirect('goods:showcart')
        except Exception as e:
            print(f"Error adding to cart: {e}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': str(e)}, status=400)
            return redirect('goods:detail', id=id)
    return redirect('goods:detail', id=id)


@login_required
def delt(request, id):
    try:
        userid = request.user.id
        cart_item = CartInfos.objects.filter(id=id, user_id=userid).first()
        if cart_item:
            cart_item.delete()
        carts = CartInfos.objects.filter(user_id=userid)
        sumlist = []
        for cart in carts:
            good = shangpin.objects.get(id=cart.shangpin_id)
            guige = Guige.objects.filter(id=cart.guige_id).first() if cart.guige_id else None
            guige_name = guige.name if guige else '随机'
            sumlist.append({
                'cart': cart,
                'good': good,
                'guige_name': guige_name
            })
        return render(request, 'cart.html', {'sumlist': sumlist})
    except Exception as e:
        print(f"删除购物车项错误: {e}")
        carts = CartInfos.objects.filter(user_id=request.user.id)
        sumlist = []
        for cart in carts:
            good = shangpin.objects.get(id=cart.shangpin_id)
            guige = Guige.objects.filter(id=cart.guige_id).first() if cart.guige_id else None
            guige_name = guige.name if guige else '无规格'
            sumlist.append({
                'cart': cart,
                'good': good,
                'guige_name': guige_name
            })
        return render(request, 'cart.html', {'sumlist': sumlist})


def batch_delete_cart(request):
    if request.method == 'POST':
        try:
            cart_ids = request.POST.getlist('cart_items')
            if not cart_ids:
                return redirect('goods:carts')
            cart_ids = [int(cid) for cid in cart_ids if cid.isdigit()]
            CartInfos.objects.filter(Q(id__in=cart_ids) & Q(user_id=request.user.id)).delete()
            userid = request.user.id
            carts = CartInfos.objects.filter(user_id=userid)
            sumlist = []
            for cart in carts:
                good = shangpin.objects.get(id=cart.shangpin_id)
                guige = Guige.objects.filter(id=cart.guige_id).first() if cart.guige_id else None
                guige_name = guige.name if guige else '随机'
                sumlist.append({
                    'cart': cart,
                    'good': good,
                    'guige_name': guige_name
                })
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'成功删除{len(cart_ids)}个商品'
                })
            return render(request, 'cart.html', {'sumlist': sumlist})
        except Exception as e:
            print(f"批量删除购物车错误: {e}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': '删除失败：' + str(e)
                }, status=400)
            return redirect('goods:showcart')
    return redirect('goods:showcart')


@login_required
def showoderinfo(request):
    userid = request.user.id
    orderinfos = OrderInfos.objects.filter(user_id=userid)
    return render(request, 'orderinfo.html', {'orderInfos': orderinfos})


@login_required
def checkout(request):
    userid = request.user.id
    selected_cart_ids = request.POST.getlist('cart_items')
    if not selected_cart_ids:
        carts = CartInfos.objects.filter(user_id=userid)
        sumlist = []
        for cart in carts:
            good = shangpin.objects.get(id=cart.shangpin_id)
            guige = Guige.objects.filter(id=cart.guige_id).first() if cart.guige_id else None
            guige_name = guige.name if guige else '随机'
            sumlist.append({
                'cart': cart,
                'good': good,
                'guige_name': guige_name
            })
        return render(request, 'cart.html', {
            'sumlist': sumlist,
            'error_msg': '请至少选择一个商品进行结算！'
        })
    carts = CartInfos.objects.filter(
        id__in=selected_cart_ids,
        user_id=userid
    )
    total_price = 0
    shangpins = []
    sumlist_data = []
    for cart in carts:
        good = shangpin.objects.get(id=cart.shangpin_id)
        shangpins.append(good)
        total_price += good.price * cart.num
        guige = Guige.objects.filter(id=cart.guige_id).first() if cart.guige_id else None
        guige_name = guige.name if guige else '随机'
        sumlist_data.append({
            'cart': cart,
            'good': good,
            'guige_name': guige_name
        })
    carts_list = list(carts)
    sumlist = zip(carts_list, shangpins)
    address_list = Address.objects.filter(user=request.user).order_by("-is_default")
    request.session['selected_cart_ids'] = selected_cart_ids
    return render(request, 'checkout.html', {
        'sumlist': sumlist,
        'total_price': total_price,
        'sumlist_data': sumlist_data,
        'address_list': address_list,
    })


@login_required
def confirm_checkout(request):
    userid = request.user.id
    selected_cart_ids = request.session.get('selected_cart_ids', [])
    if not selected_cart_ids:
        return redirect('goods:carts')
    carts = CartInfos.objects.filter(
        id__in=selected_cart_ids,
        user_id=userid
    )
    total_price = 0
    for cart in carts:
        good = shangpin.objects.get(id=cart.shangpin_id)
        total_price += good.price * cart.num
    order = OrderInfos(
        price=total_price,
        user_id=userid,
        state='待支付',
        create_time=datetime.now()
    )
    order.save()
    # 清空购物车（若需要可取消注释）
    # carts.delete()
    del request.session['selected_cart_ids']
    return render(request, 'success.html', {
        'id': order.id,
        'time': order.create_time,
    })


# 收货地址相关
@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user).order_by("-is_default")
    return render(request, "address_list.html", {"addresses": addresses})


@login_required
def address_add(request):
    if request.method == "POST":
        receiver = request.POST.get("receiver")
        phone = request.POST.get("phone")
        province = request.POST.get("province")
        city = request.POST.get("city")
        district = request.POST.get("district")
        detail = request.POST.get("detail")
        Address.objects.create(
            user=request.user,
            receiver=receiver,
            phone=phone,
            province=province,
            city=city,
            district=district,
            detail=detail
        )
        return redirect("goods:address_list")
    return render(request, "address_add.html")


@login_required
def set_default(request, id):
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    addr = get_object_or_404(Address, id=id, user=request.user)
    addr.is_default = True
    addr.save()
    return redirect("goods:address_list")


# 评价功能（仅购买用户可评价）
@login_required
def add_review(request, product_id):
    product = get_object_or_404(shangpin, id=product_id)

    # 校验用户是否购买过该商品
    paid_orders = OrderInfos.objects.filter(
        user_id=request.user.id,
        state__in=['待支付', '已支付', '已完成', '待发货', '已发货']
    )
    if not paid_orders.exists():
        messages.error(request, '仅允许购买过该商品的用户评价！')
        return redirect('goods:detail', id=product.id)

    purchased_cart_items = CartInfos.objects.filter(
        user_id=request.user.id,
        shangpin_id=product.id,
    )
    if not purchased_cart_items.exists():
        messages.error(request, '仅允许购买过该商品的用户评价！')
        return redirect('goods:detail', id=product.id)

    existing_review = ProductReview.objects.filter(user=request.user, product=product).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, '评价提交成功！' if not existing_review else '评价修改成功！')
            return redirect('goods:detail', id=product.id)
    else:
        form = ReviewForm(instance=existing_review)

    return render(request, 'add_review.html', {
        'form': form,
        'product': product,
        'existing_review': existing_review
    })


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(ProductReview, id=review_id, user=request.user)
    product_id = review.product.id
    review.delete()
    messages.success(request, '评价已成功删除！')
    return redirect('goods:detail', id=product_id)
# -------------------- 新增功能视图 --------------------

@login_required
def address_delete(request, id):
    """删除收货地址"""
    addr = get_object_or_404(Address, id=id, user=request.user)
    addr.delete()
    messages.success(request, '地址已删除')
    return redirect('goods:address_list')


@login_required
def pay_order(request, order_id):
    """模拟支付（待支付→已支付）"""
    order = get_object_or_404(OrderInfos, id=order_id, user_id=request.user.id)
    if order.state == '待支付':
        order.state = '已支付'
        order.save()
        messages.success(request, '支付成功（模拟）')
    else:
        messages.warning(request, '该订单无法支付')
    return redirect('goods:orderinfo')


@login_required
def confirm_receipt(request, order_id):
    """确认收货（已支付/发货中→已签收）"""
    order = get_object_or_404(OrderInfos, id=order_id, user_id=request.user.id)
    if order.state in ['已支付', '发货中']:
        order.state = '已签收'
        order.save()
        messages.success(request, '已确认收货')
    else:
        messages.warning(request, '订单状态不允许确认收货')
    return redirect('goods:orderinfo')


@login_required
def toggle_favorite(request, product_id):
    """收藏/取消收藏（AJAX）"""
    from .models import Favorite
    product = get_object_or_404(shangpin, id=product_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
        is_fav = False
    else:
        is_fav = True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_fav': is_fav, 'count': Favorite.objects.filter(product=product).count()})
    return redirect('goods:detail', id=product_id)