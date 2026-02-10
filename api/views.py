from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from sslcommerz_lib import SSLCOMMERZ 
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings as django_settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect

@api_view(['POST'])
def initate_payment(request):
    user = request.user 
    amount = request.data.get('amount')
    order_id = request.data.get('order_id')
    settings = { 'store_id': 'perso6989c113449b1', 'store_pass': 'perso6989c113449b1@ssl', 'issandbox': True }
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = amount
    post_body['currency'] = "BDT"
    post_body['tran_id'] = f'trx_{order_id}_{user.id}'
    post_body['success_url'] = django_settings.BACKEND_URL + "payment_success"
    post_body['fail_url'] = django_settings.BACKEND_URL + "payment_fail"
    post_body['cancel_url'] = django_settings.BACKEND_URL + "payment_cancel"
    post_body['emi_option'] = 0
    post_body['cus_name'] = user.first_name + " " + user.last_name
    post_body['cus_email'] = user.email
    post_body['cus_phone'] = user.phone_number
    post_body['cus_add1'] = user.address
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Hotel Booking"
    post_body['product_category'] = "Hotel"
    post_body['product_profile'] = "general"

    response = sslcz.createSession(post_body) 
    if response.get('status') == 'SUCCESS':
        return Response({'url': response['GatewayPageURL']})   
    else:
        return Response({'error': 'Payment failed'})
    

@api_view(['POST', 'GET'])
def payment_success(request):
    # print("request: ", request.data.get('tran_id').split('_')[2])
    user_id = request.data.get('tran_id').split('_')[2]
    if user_id:
        user = User.objects.get(id=user_id)
        user.balance += int(request.data.get('total_amount'))
        user.save()
        return HttpResponseRedirect(f"{django_settings.FRONTEND_URL}dashboard/payment?status=success")
    return HttpResponseRedirect(f"{django_settings.FRONTEND_URL}dashboard/payment?status=fail")

@api_view(['POST'])
def payment_fail(request):
    return HttpResponseRedirect(f"{django_settings.FRONTEND_URL}dashboard/payment?status=fail")

@api_view(['POST'])
def payment_cancel(request):
    return HttpResponseRedirect(f"{django_settings.FRONTEND_URL}dashboard/payment?status=cancel")


