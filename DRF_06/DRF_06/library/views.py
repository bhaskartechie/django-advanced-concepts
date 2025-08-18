"""
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Book
import json

def book_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    books = Book.objects.all()
    data = [
        {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "publication_year": book.publication_year
        } for book in books
    ]
    return JsonResponse({"books": data})

def book_detail(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    try:
        book = Book.objects.get(pk=pk)
        data = {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "publication_year": book.publication_year
        }
        return JsonResponse(data)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Book not found"}, status=404)

@csrf_exempt
@login_required
def book_create(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        title = data.get("title")
        author = data.get("author")
        isbn = data.get("isbn")
        publication_year = data.get("publication_year")
        if not all([title, author, isbn, publication_year]):
            return JsonResponse({"error": "All fields required"}, status=400)
        if Book.objects.filter(isbn=isbn).exists():
            return JsonResponse({"error": "ISBN must be unique"}, status=400)
        book = Book.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            publication_year=publication_year
        )
        return JsonResponse({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "publication_year": book.publication_year
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@login_required
def book_update(request, pk):
    if request.method not in ["PUT", "PATCH"]:
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        book = Book.objects.get(pk=pk)
        data = json.loads(request.body)
        book.title = data.get("title", book.title)
        book.author = data.get("author", book.author)
        book.isbn = data.get("isbn", book.isbn)
        book.publication_year = data.get("publication_year", book.publication_year)
        if Book.objects.filter(isbn=book.isbn).exclude(pk=pk).exists():
            return JsonResponse({"error": "ISBN must be unique"}, status=400)
        book.save()
        return JsonResponse({
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "isbn": book.isbn,
            "publication_year": book.publication_year
        })
    except Book.DoesNotExist:
        return JsonResponse({"error": "Book not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@login_required
def book_delete(request, pk):
    if request.method != "DELETE":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        book = Book.objects.get(pk=pk)
        book.delete()
        return JsonResponse({"message": "Book deleted"}, status=204)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Book not found"}, status=404)

"""

from rest_framework import viewsets
from .models import Book
from .serializers import BookSerializer
from .permissions import IsStaffOrReadOnly
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer


# API endpoint for visitor registration using CustomUser
class UserRecordView(APIView):
    def post(self, request):
        data = request.data
        userid = data.get('userid')
        email = data.get('email')
        # Check if user already exists
        if (
            CustomUser.objects.filter(userid=userid).exists()
            or CustomUser.objects.filter(email=email).exists()
        ):
            return Response(
                {'detail': 'User already exists.'}, status=status.HTTP_200_OK
            )
        serializer = CustomUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsStaffOrReadOnly]
    search_fields = ['title', 'author']
    filterset_fields = ['publication_year']
