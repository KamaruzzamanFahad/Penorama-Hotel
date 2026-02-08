from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from hotelroom.models import HotelRoom, Review, HotelRoomImage, Hotel,  Booking
from hotelroom.serializer import HotelRoomModelSerializer,HotelModelSerializer, BookingSerializer, ReviewSerializer, HotelRoomImageSerializer
from django.db.models import Count, Sum, Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend 
from hotelroom.filters import HotelRoomFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from hotelroom.paginstions import HotelPagination 
from rest_framework.permissions import IsAdminUser, AllowAny, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly, IsAuthenticated
from api.permissitions import IsAdminOrReadOnly,FullDjangoModelPermissition
from hotelroom.permissitions import IsReviewAuthorOrReadOnly
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from users.models import User



class HotelViewSet(ModelViewSet):
    queryset = Hotel.objects.prefetch_related('reviews').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'address']
    pagination_class = HotelPagination 
    permission_classes =[IsAdminOrReadOnly]
    
    serializer_class = HotelModelSerializer

class HotelRoomViewSet(ModelViewSet):
    # queryset = HotelRoom.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = HotelRoomFilter 
    search_fields = ['room_number', 'description']
    ordering_fields = ['price_per_night']
    pagination_class = HotelPagination 
    permission_classes =[IsAdminOrReadOnly]

    def perform_create(self, serializer):
        hotel_id = self.kwargs.get('hotel_pk')
        serializer.save(hotel_id=hotel_id)
    def get_queryset(self):
        return HotelRoom.objects.filter(hotel_id=self.kwargs['hotel_pk'])
    
    serializer_class = HotelRoomModelSerializer

class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(hotelroom_id=self.kwargs['room_pk'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        context['hotelroom'] = HotelRoom.objects.get(id=self.kwargs['room_pk'])
        check_in = self.request.data.get('check_in')
        check_out = self.request.data.get('check_out')
        if check_in and check_out:
            hotelroom = context['hotelroom']
            days = (self.extractdays(check_out) - self.extractdays(check_in)).days
            context['total_cost'] = hotelroom.price_per_night * max(days, 1)
        else:
            context['total_cost'] = 0
        return context

    def extractdays(self, date_str):
        from datetime import datetime
        return datetime.strptime(date_str, '%Y-%m-%d').date()

    def perform_create(self, serializer):
        serializer.save()
        subject = f"Booking Confirmation for {self.request.user.first_name} {self.request.user.last_name}"
        message = f"Hi {self.request.user.first_name} {self.request.user.last_name}, Your booking has been confirmed"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [self.request.user.email])
        

class HotelRoomImageViewSet(ModelViewSet):
    serializer_class = HotelRoomImageSerializer
    permission_classes =[IsAdminOrReadOnly]

    def get_queryset(self):
        return HotelRoomImage.objects.filter(hotelroom_id = self.kwargs['room_pk'])
    
    def perform_create(self, serializer):
        serializer.save(hotelroom_id = self.kwargs['room_pk'])

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes =[IsReviewAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Review.objects.filter(hotel_id=self.kwargs['hotel_pk'])

    def get_serializer_context(self):
        return {'hotel_id': self.kwargs['hotel_pk']}


class AllReviewViewSet(ModelViewSet):
    queryset = Review.objects.prefetch_related('hotel').all()
    serializer_class = ReviewSerializer

class SpecificUserSpecificHotelReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes =[IsAuthenticated]

    def get_queryset(self):
        hotel_id = self.request.query_params.get('hotel_id')
        return Review.objects.filter(
            user=self.request.user,
            hotel_id=hotel_id
        )


class AdminStatisticsViewSet(APIView):
    permission_classes =[IsAdminUser]
    def get(self, request):
        try:
            now = timezone.now()
            
            first_day_of_current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_day_of_prev_month = first_day_of_current_month - timedelta(days=1)
            first_day_of_prev_month = last_day_of_prev_month.replace(day=1)
            start_of_week = now - timedelta(days=now.weekday())

            current_month_sales = Booking.objects.filter(
                booking_date__gte=first_day_of_current_month
            ).aggregate(total=Sum('total_cost'))['total'] or 0

            prev_month_sales = Booking.objects.filter(
                booking_date__gte=first_day_of_prev_month,
                booking_date__lte=last_day_of_prev_month
            ).aggregate(total=Sum('total_cost'))['total'] or 0

            bookings_this_week = Booking.objects.filter(
                booking_date__gte=start_of_week
            ).count()

            bookings_this_month = Booking.objects.filter(
                booking_date__gte=first_day_of_current_month
            ).count()

            most_booked_rooms = HotelRoom.objects.annotate(
                booking_count=Count('booking')
            ).order_by('-booking_count')[:5]

            most_booked_rooms_data = [
                {
                    "hotel": room.hotel.name if room.hotel else None,
                    "room_number": room.room_number,
                    "booking_count": room.booking_count
                } for room in most_booked_rooms
            ]

            top_customers = User.objects.annotate(
                total_spent=Sum('booking__total_cost')
            ).filter(total_spent__gt=0).order_by('-total_spent')[:5]

            top_customers_data = [
                {
                    "email": user.email,
                    "first_name": user.first_name,
                    "total_spent": float(user.total_spent) if user.total_spent else 0
                } for user in top_customers
            ]

            return Response({
                "sales": {
                    "current_month": float(current_month_sales),
                    "previous_month": float(prev_month_sales),
                },
                "bookings_count": {
                    "this_week": bookings_this_week,
                    "this_month": bookings_this_month,
                },
                "most_booked_rooms": most_booked_rooms_data,
                "top_customers": top_customers_data,
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)





    