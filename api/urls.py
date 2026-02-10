from django.urls import path, include
from hotelroom.views import HotelRoomViewSet,AllReviewViewSet,SpecificUserSpecificHotelReviewViewSet,AdminStatisticsViewSet, ReviewViewSet, HotelRoomImageViewSet, HotelViewSet, BookingViewSet
from rest_framework_nested import routers
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from api.views import initate_payment, payment_success, payment_fail, payment_cancel

schema_view = get_schema_view(
   openapi.Info(
      title="Panorama HotelRoom API",
      default_version='v1',
      description="Panorama HotelRoom API",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="mihacker41@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register('hotels', HotelViewSet, basename='hotels')
router.register('reviews', AllReviewViewSet, basename='all-reviews')
router.register('my-hotel-reviews', SpecificUserSpecificHotelReviewViewSet, basename='my-hotel-reviews')

hotel_router = routers.NestedDefaultRouter(router, 'hotels', lookup='hotel')
hotel_router.register('rooms', HotelRoomViewSet, basename='hotel-rooms')
hotel_router.register('reviews', ReviewViewSet, basename='hotel-reviews')

room_router = routers.NestedDefaultRouter(hotel_router, 'rooms', lookup='room')
room_router.register('images', HotelRoomImageViewSet, basename='room-images')
room_router.register('booking', BookingViewSet, basename='room-booking')

urlpatterns = [
    path('', include(router.urls)), 
    path('', include(hotel_router.urls)), 
    path('', include(room_router.urls)),
    path('admin-statistics/', AdminStatisticsViewSet.as_view(), name='admin-statistics'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('initiate-payment/', initate_payment, name='initiate-payment'),
    path('payment_success/', payment_success, name='payment_success'),
    path('payment_fail/', payment_fail, name='payment_fail'),
    path('payment_cancel/', payment_cancel, name='payment_cancel'),
]