from rest_framework import serializers
from note.models import Note, Labels, Categories, Attachments, Colors
from django.contrib.auth.models import User, Group


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer only for POST request to create a new user
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user requests excluding POST request
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class LabelsSerializer(serializers.ModelSerializer):
    """
    Serializer for public view notes list
    """
    class Meta:
        model = Labels
        fields = ('id', 'title')


class CategoriesForNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for public view notes list
    """
    class Meta:
        model = Categories
        fields = ('id', 'title')


class AttachmentPublicSerilizer(serializers.ModelSerializer):
    """
    Serializer for public detail view of a note
    """
    class Meta:
        model = Attachments
        fields = ('file', 'title')


class NotePublicListSerializer(serializers.ModelSerializer):
    """
    Serializer for public list access to notes.
    """
    color = serializers.StringRelatedField()
    category = CategoriesForNoteSerializer(many=True)
    label = LabelsSerializer(many=True)

    class Meta:
        model = Note
        fields = ('id', 'title', 'color', 'category', 'label')


class NotePublicSingleSerializer(serializers.ModelSerializer):
    """
    Serializer for public access to a single note
    """
    color = serializers.StringRelatedField(allow_null=True, required=False)
    category = CategoriesForNoteSerializer(many=True)
    label = LabelsSerializer(many=True)
    owner = serializers.StringRelatedField()
    file = AttachmentPublicSerilizer(many=True)

    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'color', 'category', 'label', 'owner', 'file')


class NoteUserListSerializer(serializers.ModelSerializer):
    """
    Serializer for user list access.
    """
    color = serializers.StringRelatedField()
    category = CategoriesForNoteSerializer(many=True)
    label = LabelsSerializer(many=True)
    delegated = UserSerializer(many=True)

    class Meta:
        model = Note
        fields = ('id', 'title', 'color', 'category', 'label', 'delegated')


class NotesUserSingleSerializer(serializers.ModelSerializer):
    """
    Basic serializer for create a note
    """
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    color = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Colors.objects.all(), required=False)
    category = serializers.PrimaryKeyRelatedField(many=True, queryset=Categories.objects.all(), required=False)
    delegated = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    label = serializers.PrimaryKeyRelatedField(many=True, queryset=Labels.objects.all(), required=False)
    file = serializers.PrimaryKeyRelatedField(many=True, queryset=Attachments.objects.all(), required=False)

    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'color', 'category', 'label', 'owner', 'delegated', 'file')


class NotesEditSerializer(serializers.ModelSerializer):
    """
    This serializer returns 3 edition parameters:
    labels - list of available labels
    files - list of available authorized users fies
    users - list of available users for delegate them permission to edit the note
    """
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    color = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Colors.objects.all(), required=False)
    category = serializers.PrimaryKeyRelatedField(many=True, queryset=Categories.objects.all(), required=False)
    delegated = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    label = serializers.PrimaryKeyRelatedField(many=True, queryset=Labels.objects.all(), required=False)
    file = serializers.PrimaryKeyRelatedField(many=True, queryset=Attachments.objects.all(), required=False)
    labels = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ('id', 'title', 'content', 'color', 'category', 'label', 'owner', 'delegated', 'file', 'labels',
                  'files', 'users')

    def get_labels(self, obj):
        """
        returns a list of available labels
        """
        return LabelsSerializer(Labels.objects.all(), many=True).data

    def get_files(self, obj):
        """
        returns a list of downloaded attachments of the authenticated user
        """
        attachments = Attachments.objects.filter(
                owner=self.context['request'].user
        ).only('id', 'title', 'file').order_by('title')
        return [{'id': i.id, 'title': i.title, 'file': i.file.url} for i in attachments]

    def get_users(self, obj):
        """
        returns a list of users for delegate permissions to a note
        """
        users = User.objects.only('id', 'username').order_by('username').exclude(username=obj.owner.username)
        return [{'id': i.id, 'username': i.username} for i in users]


class RecursiveSerializer(serializers.RelatedField):
    """
    serializer for getting hierarchic structure of the categories
    """
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CategoriesHierarchySerializer(serializers.ModelSerializer):
    """
    Serializer only for categories list
    """
    sub_category = RecursiveSerializer(many=True, read_only=True)

    class Meta:
        model = Categories
        fields = ('id', 'title', 'parent', 'sub_category')


class CategoriesSerializer(serializers.ModelSerializer):
    """
    Serializer for categories
    """

    class Meta:
        model = Categories
        fields = ('id', 'title', 'parent')


class AttachmentsSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and create files
    """
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Attachments
        fields = ('id', 'title', 'file', 'owner')


class AttachmentEditSerializer(serializers.ModelSerializer):
    """
    serializer for editing title of attachment only
    """

    class Meta:
        model = Attachments
        fields = ('id', 'title')
