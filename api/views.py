from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from sslcommerz_lib import SSLCOMMERZ 
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings as django_settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from rest_framework.permissions import IsAuthenticated



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    user = request.user
    amount = request.data.get('amount')
    order_id = request.data.get('order_id')

    if not amount or not order_id:
        return Response({'error': 'Invalid data'}, status=400)

    ssl_settings = {
        'store_id': 'perso6989c113449b1',
        'store_pass': 'perso6989c113449b1@ssl',
        'issandbox': True,
    }

    sslcz = SSLCOMMERZ(ssl_settings)

    post_body = {
        'total_amount': amount,
        'currency': 'BDT',
        'tran_id': f"trx_{order_id}_{user.id}",
        'success_url': django_settings.BACKEND_URL + 'payment_success/',
        'fail_url': django_settings.BACKEND_URL + 'payment_fail/',
        'cancel_url': django_settings.BACKEND_URL + 'payment_cancel/',
        'emi_option': 0,
        'cus_name': f"{user.first_name} {user.last_name}",
        'cus_email': user.email,
        'cus_phone': user.phone_number or 'N/A',
        'cus_add1': user.address or 'N/A',
        'cus_city': 'Dhaka',
        'cus_country': 'Bangladesh',
        'shipping_method': 'NO',
        'num_of_item': 1,
        'product_name': 'Assignment Payment',
        'product_category': 'Service',
        'product_profile': 'general',
    }

    response = sslcz.createSession(post_body)

    if response.get('status') == 'SUCCESS':
        return Response({'url': response.get('GatewayPageURL')})

    return Response({'error': 'Payment failed'}, status=400)


@api_view(['POST'])
def payment_success(request):
    tran_id = request.POST.get('tran_id') or request.GET.get('tran_id')
    amount = request.POST.get('total_amount') or request.GET.get('total_amount')

    if not tran_id or not amount:
        return HttpResponseRedirect(
            f"{django_settings.FRONTEND_URL}dashboard/payment?status=fail"
        )

    try:
        user_id = tran_id.split('_')[2]
    except:
        return HttpResponseRedirect(
            f"{django_settings.FRONTEND_URL}dashboard/payment?status=fail"
        )

    from django.contrib.auth.models import User
    user = User.objects.get(id=user_id)
    user.balance += int(float(amount))
    user.save()

    return HttpResponseRedirect(
        f"{django_settings.FRONTEND_URL}dashboard/payment?status=success"
    )


@api_view(['POST'])
def payment_fail(request):
    return HttpResponseRedirect(
        f"{django_settings.FRONTEND_URL}dashboard/payment?status=fail"
    )


@api_view(['POST'])
def payment_cancel(request):
    return HttpResponseRedirect(
        f"{django_settings.FRONTEND_URL}dashboard/payment?status=cancel"
    )
