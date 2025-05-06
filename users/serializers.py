from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'old_password', 'new_password')
        read_only_fields = ('id',)
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False}
        }

    def validate(self, data):
        if 'new_password' in data and not data.get('old_password'):
            raise serializers.ValidationError({'old_password': 'Old password is required to set new password'})
        if 'old_password' in data and not data.get('new_password'):
            raise serializers.ValidationError({'new_password': 'New password is required'})
        return data

    def update(self, instance, validated_data):
        old_password = validated_data.pop('old_password', None)
        new_password = validated_data.pop('new_password', None)

        if old_password and new_password:
            if not instance.check_password(old_password):
                raise serializers.ValidationError({'old_password': 'Wrong password'})
            instance.set_password(new_password)

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
