from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from note import views

router = DefaultRouter()
router.register(r'labels', views.LabelViewSet, base_name='labels')
router.register(r'categories', views.CategoryViewSet, base_name='categories')
router.register(r'users', views.UserViewSet, base_name='users')
router.register(r'notes', views.NotePublicViewSet, base_name='notes')
router.register(r'my_notes', views.NoteViewSet, base_name='my_notes')
router.register(r'attachments', views.AttachmentsViewSet, base_name='attachments')
router.register(r'user_registration', views.UserRegistration, base_name='user_registration')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),

]

