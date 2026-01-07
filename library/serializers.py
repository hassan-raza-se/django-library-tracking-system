from rest_framework import serializers
from .models import Author, Book, Member, Loan
from django.contrib.auth.models import User
from datetime import timedelta

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), source='author', write_only=True
    )

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'author_id', 'isbn', 'genre', 'available_copies']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = Member
        fields = ['id', 'user', 'user_id', 'membership_date']

class LoanSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source='book', write_only=True
    )
    member = MemberSerializer(read_only=True)
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(), source='member', write_only=True
    )

    class Meta:
        model = Loan
        fields = ['id', 'book', 'book_id', 'member', 'member_id', 'loan_date', 'return_date', 'is_returned']


class ExtendDateSerializer(LoanSerializer):
    additional_days = serializers.IntegerField(min_value=1, write_only=True)

    def validate_additional_days(self, additional_days):
        
        if not additional_days:
            raise serializers.ValidationError('additional_days is required in payload')
        
        if self.instance.is_returned:
            raise serializers.ValidationError('Load already returned')
        
        if self.instance.is_overdue:
            raise serializers.ValidationError('Loan already overdue')

        return additional_days

    def update(self, instance, validated_data):
        instance.due_date += timedelta(days=validated_data['additional_days']) 
        instance.save()
        return instance
    
    class Meta:
        model = Loan
        fields = ['id', 'book', 'book_id', 'member', 'member_id', 'loan_date', 'return_date', 'is_returned', 'additional_days', 'due_date']


class TopActiveMemberSerializer(serializers.ModelSerializer):
    
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    active_loans = serializers.IntegerField()

    class Meta:
        model = Member
        fields = ['id', 'username', 'email', 'active_loans']
