from django_filters.rest_framework import FilterSet
from hotelroom.models import HotelRoom

class HotelRoomFilter(FilterSet):
    class Meta:
        model = HotelRoom
        fields = {
            'price_per_night': ['exact', 'gt', 'lt'],
        }

