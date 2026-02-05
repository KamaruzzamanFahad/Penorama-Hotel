from rest_framework import serializers
from decimal import Decimal
from hotelroom.models import HotelRoom, Review, HotelRoomImage, Hotel, Booking
from users.models import User

class HotelModelSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    review = serializers.SerializerMethodField(method_name='get_review')
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'address', 'description', 'image', 'review']

    def get_review(self, obj):
        return ReviewSerializer(obj.reviews.all(), many=True).data


class HotelRoomImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = HotelRoomImage
        fields = ['id', 'image']


class HotelRoomModelSerializer(serializers.ModelSerializer):
    images = HotelRoomImageSerializer(many=True, read_only=True)
    hotel = HotelModelSerializer(read_only=True)
    class Meta:
        model = HotelRoom
        fields = ['id', 'hotel', 'room_number', 'room_type', 'price_per_night', 'description', 'images', 'status']
    

    def validate_price(self, price_per_night):
        if price_per_night < 0:
            raise serializers.ValidationError("Price cannot be negative")
        if price_per_night > 1000000:
            raise serializers.ValidationError("Price cannot be greater than 1000000")
        return price_per_night

    def create(self, validated_data):   
        hotel_id = validated_data.get('hotel_id') 
        return super().create(validated_data)

    

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'user', 'hotelroom', 'booking_date', 'check_in', 'check_out', 'total_cost']
        read_only_fields = ['user', 'hotelroom', 'booking_date', 'total_cost']

    def validate(self, attrs):
        user = self.context['user']
        hotelroom = self.context['hotelroom']
        total_cost = self.context['total_cost']

        check_in = attrs.get('check_in')
        check_out = attrs.get('check_out')

        if check_out <= check_in:
            raise serializers.ValidationError("Check out date must be after check in date")

        if user.balance < total_cost:
            raise serializers.ValidationError("Insufficient balance")

        if hotelroom.status == True:
            raise serializers.ValidationError("Hotel room is already booked")
        return attrs

    def create(self, validated_data):
        user = self.context['user']
        hotelroom = self.context['hotelroom']
        total_cost = self.context['total_cost']

        user.balance -= total_cost
        user.save()

        hotelroom.status = True
        hotelroom.save()

        validated_data['user'] = user
        validated_data['hotelroom'] = hotelroom
        validated_data['total_cost'] = total_cost

        return Booking.objects.create(**validated_data)


class ReviewUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(method_name='get_current_user_name')
    class Meta:
        model = User
        fields = ['id', 'name']

    def get_current_user_name(salf,obj):
        return obj.get_full_name()
        

    

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(method_name='get_user')

    class Meta:
        model = Review
        fields = ['id', 'user', 'hotel', 'rattings', 'comment']
        read_only_fields = ['user', 'hotel']

    def get_user(self, obj):
        return ReviewUserSerializer(obj.user).data

        

    def create(self, validated_data):
        hotel_id = self.context['hotel_id']
        return Review.objects.create(hotel_id=hotel_id, **validated_data)