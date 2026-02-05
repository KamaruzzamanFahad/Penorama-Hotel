from django.db import models
from users.models import User
from  django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from cloudinary.models import CloudinaryField


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    description = models.TextField()
    image = CloudinaryField('image')

    def __str__(self):
        return self.name

class HotelRoom(models.Model):
    Room_Type = [
        ('Single', 'Single'),
        ('Double', 'Double'),
        ('Suite', 'Suite'),
    ]
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_number = models.IntegerField()
    room_type = models.CharField(max_length=100, choices=Room_Type)
    description = models.TextField(blank=True, null=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hotel.name} - {str(self.room_number)}" 

class HotelRoomImage(models.Model):
    hotelroom = models.ForeignKey(HotelRoom, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image')


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotelroom = models.ForeignKey(HotelRoom, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    check_in = models.DateField()
    check_out = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.first_name} booked {self.hotelroom.room_number}"



class Review(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    rattings = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

    def __str__(self):
        return f"Review By {self.user.first_name} on {self.hotel.name}"