from rest_framework import serializers
from .models import User, UserSession


class UserSerializer(serializers.ModelSerializer):
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'service_number', 'rank', 'rank_display',
            'role', 'role_display', 'contact_number', 'profile_picture',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'full_name', 'service_number', 'rank', 'role',
            'contact_number', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UserSessionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_rank = serializers.CharField(source='user.get_rank_display', read_only=True)
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'user', 'user_name', 'user_rank', 'session_key',
            'ip_address', 'user_agent', 'is_active', 'created_at', 'last_activity'
        ]
        read_only_fields = ['id', 'created_at', 'last_activity']
