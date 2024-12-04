from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group, Permission
from .models import UserProfile
from apps.iPM.models import Dashboard
from rest_framework import serializers


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data['email'],
        )
        return user

    def validate_email(self, value):
        return value.lower()
    
class UserListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class GroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class PermissionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        username = data.get('username', '')
        password = data.get('password', '')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError("User account is disabled.")
            else:
                raise serializers.ValidationError("Unable to login with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")

        return data
    
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email')
    group = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    is_staff = serializers.BooleanField(source='user.is_staff', read_only=True)
    is_superadmin = serializers.BooleanField(source='user.is_superuser', read_only=True)
    dashboards = serializers.PrimaryKeyRelatedField(many=True, queryset=Dashboard.objects.all(), required=False)

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'username',
            'name',
            'email',
            'phone',
            'description',
            'employee_id',
            'department_team',
            'immediate_head_name',
            'immediate_head_phone',
            'user',
            'group',
            'permissions',
            'is_staff',  
            'is_superadmin',
            'dashboards',
        )

    def get_name(self, obj):
        first_name = obj.user.first_name
        last_name = obj.user.last_name
        return f"{first_name} {last_name}".strip()

    def get_group(self, obj):
        return [group.name for group in obj.user.groups.all()]

    def get_permissions(self, obj):
        permissions = set()
        for group in obj.user.groups.all():
            for perm in group.permissions.all():
                permissions.add(perm.codename)
        
        # Add user-specific permissions
        for perm in obj.user.user_permissions.all():
            permissions.add(perm.codename)

        return list(permissions)

    def create(self, validated_data):
        dashboards_data = validated_data.pop('dashboards', [])
        user_profile = super().create(validated_data)
        
        # Handle the ManyToMany field separately
        if dashboards_data:
            user_profile.dashboards.set(dashboards_data)
        
        return user_profile

    def update(self, instance, validated_data):
        dashboards_data = validated_data.pop('dashboards', [])
        user_profile = super().update(instance, validated_data)
        
        # Handle the ManyToMany field separately
        if dashboards_data:
            user_profile.dashboards.set(dashboards_data)

        return user_profile


class UserProfileListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email')
    # usergroup = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'username',
            'name',
            'email',
            'phone',
            'description',
            'user',
            # 'usergroup',
        )

    def get_name(self, obj):
        first_name = obj.user.first_name
        last_name = obj.user.last_name
        return f"{first_name} {last_name}".strip()  # Concatenate first and last name, strip any extra spaces

    # def get_usergroup(self, obj):
    #     return [group.name for group in obj.user.groups.all()]  # Get the names of the groups the user belongs to

class UserNameSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('user', 'name')

    def get_name(self, obj):
        first_name = obj.user.first_name
        last_name = obj.user.last_name
        return f"{first_name} {last_name}".strip()
