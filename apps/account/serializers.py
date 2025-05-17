from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer

User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Serializer for creating a new user.
    """

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ['id', 'email', 'username', 'password', 'first_name', 'last_name', 'id_no', 'security_question',
                  'security_answer']

    def create(self, validated_data):
        """
        Create a new user instance.
        """
        return User.objects.create_user(**validated_data)
