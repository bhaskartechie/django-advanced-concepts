from rest_framework import serializers
from .models import Book, CustomUser

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'publication_year']

    def validate_isbn(self, value):
        if Book.objects.filter(isbn=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("ISBN must be unique")
        return value


# Serializer for CustomUser
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['userid', 'firstname', 'email', 'gender', 'notified']