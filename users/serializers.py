from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'password2', 'email', 
                 'first_name', 'last_name', 'phone_number')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Parollar bir xil emas"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'old_password', 'new_password')
        read_only_fields = ('id',)
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False}
        }

    def validate(self, data):
        if 'new_password' in data and not data.get('old_password'):
            raise serializers.ValidationError(
                {'old_password': "Yangi parol o'rnatish uchun eski parol talab qilinadi"}
            )
        if 'old_password' in data and not data.get('new_password'):
            raise serializers.ValidationError(
                {'new_password': "Yangi parol kiritish talab qilinadi"}
            )
        return data

    def update(self, instance, validated_data):
        old_password = validated_data.pop('old_password', None)
        new_password = validated_data.pop('new_password', None)

        if old_password and new_password:
            if not instance.check_password(old_password):
                raise serializers.ValidationError(
                    {'old_password': "Noto'g'ri parol"}
                )
            instance.set_password(new_password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

        return super().update(instance, validated_data)

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'phone_number')
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
