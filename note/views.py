from django.contrib.auth.models import User, Group
from django.db.models import Q
from rest_framework import viewsets, status, generics, mixins, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import detail_route, list_route, permission_classes
from rest_framework.response import Response
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope, TokenHasScope
from note import serializers
from note.models import Colors, Labels, Categories, Note, Attachments
from note.permissions import CustomNotesPermissions, OwnerPermissions


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination class for 'unlimited' count of objects.
    """
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    endpoint List of users
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserRegistration(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Endpoint for user registration
    /user_registration/
    /user_registration.json - method POST
    params: {"username", "email", "first_name", "last_name", "password"}
    password and username are required

    """
    queryset = User.objects.all()
    serializer_class = serializers.UserCreateSerializer


class NotePublicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint for public access to list of notes and single note.

    1.

        base_host/notes.json
        base_host/notes/?format=json

    list notes, methods 'GET', 'HEAD', 'OPTIONS'.

    2.

        base_host/notes/{id}.json
        base_host/notes/{id}/?format=json

    single note, methods 'GET', 'HEAD', 'OPTIONS'.
    """
    queryset = Note.objects.all()
    serializer_class = serializers.NotePublicListSerializer

    def list(self, request, *args, **kwargs):
        queryset = Note.objects.only('id', 'title', 'color', 'category', 'owner')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = serializers.NotePublicSingleSerializer(instance)
        return Response(serializer.data)


class NoteViewSet(viewsets.ModelViewSet):
    """
    Endpoints for authenticated users to manage their notes:

    1.

        base_host/my_notes.json
        base_host/my_notes/?format=json

    method GET returns a users notes list including delegated notes to him.
    Returns:
         { "id", "title", "content", "color", "category", "label", "owner", "delegated",
    "file", "labels", "files", "users"}

     method POST is for creating a new note.
    Params for a new note (method POST):

        title = CharField(max_length=200)
        content = CharField(required)
        color = color id (foreignkey)
        category = category id (many to many)
        label = label id (many to many)
        delegated = user id (many to many)
        file = attachment id (many to many)

    2.

        base_host/my_notes/{id}.json
        base_host/my_notes/{id}?format=json

    method GET for detail view.
    Returns:

        { "id", "title", "content", "color", "category", "label", "owner", "delegated",
        "file", "labels", "files", "users"}

    and edition fields:

        labels - list of labels [{ "id": "value", "title": "value"}]
        files - list of attachments [{ "file": "path to file without domain", "title": "Title", "id": "value" }]
        users - list of users [{"id": "value", "username": "value"}]

    method PUT is for update an instance
    only "content" - is required field

    method DELETE allows to delete the users notes, not delegated notes.
    """
    queryset = Note.objects.all()
    serializer_class = serializers.NotesEditSerializer
    permission_classes = (permissions.IsAuthenticated, CustomNotesPermissions)

    def list(self, request, *args, **kwargs):
        # show the notes where user is owner and has delegated permissions
        queryset = self.filter_queryset(self.get_queryset()).filter(
                Q(owner=request.user) | Q(delegated__username__exact=request.user.get_username())
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.NoteUserListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializers.NoteUserListSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Labels.objects.all()
    serializer_class = serializers.LabelsSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Endpoint for categories.

    1.

        /categories.json
        /categories/?format=json

    GET method returns a list of hierarchical data of categories
    POST method for creating a new category. Accepts two parameters:

        "title" - category name (required)
        "parent_id" - id of parent category

    2.

        /categories/{id}.json
        /categories/{id}/?format=json

    GET method returns category { "id": "id", "title": "value", "parent": "parent category id or null"}.
    PUT method for creating accepts the same parameters as GET.
    DELETE method will remove all sub_categories too.

    """
    queryset = Categories.objects.all()  # .filter(parent=None).order_by('id')
    serializer_class = serializers.CategoriesSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        """
        Overriding list method for displaying hierarchical data
        """
        queryset = Categories.objects.filter(parent=None).order_by('id')
        serializer = serializers.CategoriesHierarchySerializer(queryset, many=True)
        return Response(serializer.data)


class AttachmentsViewSet(viewsets.ModelViewSet):
    """
    Endpoint for all attachments if it need

    1.

        /attachments.json
        /attachments/?format=json

    method GET returns a list of users items

        {"id": "value", "title": "title", "file": "path to file without domain", "owner": id}

    method POST - create an attachment

        {"title", "file"}

    2.

        /attachments/{id}.json
        /attachments/{id}/?format=json

    Method GET return the same as previous but for a single file.
    Method PUT allows to edit only "title".
    Method DELETE removes the attachment.

    """
    queryset = Attachments.objects.all()
    serializer_class = serializers.AttachmentsSerializer
    permission_classes = (permissions.IsAuthenticated, OwnerPermissions)

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return serializers.AttachmentEditSerializer
        return serializers.AttachmentsSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(Attachments.objects.filter(owner=request.user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
