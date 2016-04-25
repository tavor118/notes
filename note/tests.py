from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate
from django.contrib.auth.models import User


class UserTests(APITestCase):

    def setUp(self):
        self.data = {'username': 'mike', 'first_name': 'Mike', 'last_name': 'Tyson', 'password': 'secret'}

    def test_create_account(self):
        """
        Ensure we can create a new user object.
        """
        response = self.client.post('/user_registration/', self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, self.data['username'])


class UnauthorizedTest(APITestCase):
    def test_create_label(self):
        """
        Unauthorized user cannot create a label
        """
        data = {'title': 'work'}
        response = self.client.post('/labels/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category(self):
        """
        Unauthorized user cannot create a category
        """
        data = {'title': 'New category'}
        response = self.client.post('/categories/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class NoteTest(APITestCase):

    def setUp(self):
        data = {'username': 'mike', 'first_name': 'Mike', 'last_name': 'Tyson', 'password': 'secret'}
        data2 = {'username': 'second', 'first_name': 'Can_look', 'last_name': 'into_tomorrow', 'password': 'secret'}
        self.client.post('/user_registration/', data, format='json')
        self.client.post('/user_registration/', data2, format='json')
        self.user = User.objects.get(username='mike')

    def test_create_label(self):
        """
        Authorized user can create a label
        """
        data = {'title': 'work'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/labels/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_category(self):
        """
        Authorized user can create a category
        """
        data = {'title': 'New category'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/categories/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response2 = self.client.post('/categories/', {'title': 'sub', 'parent': 1}, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    def test_create_note(self):
        """
        Authorized user can create a note
        """
        data = {'content': 'Content of the note'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/my_notes/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class NoteDelegatedTest(APITestCase):
    pass
    # def test_delegate_note(self):
    #     """
    #     Authorized user can delegate his note to another user
    #     """
    #     pass
    #
    # def test_edit_delegated_note(self):
    #     """
    #     Authorized user can edit a note that was delegated to him
    #     """
    #     pass
    #
    # def test_delete_delegated_note(self):
    #     """
    #     Authorized user cannot delete a note that was delegated to him
    #     """
    #     pass
    #
    # def test_edit_another_note(self):
    #     """
    #     Authorized user cannot edit a note that was created by another
    #     user without delegated permissions
    #     """
    #     pass
    #
    # def test_create_an_attachment(self):
    #     """
    #     Authorized user can create an attachment
    #     """
    #     pass
    #
    # def test_show_list_another_attachments(self):
    #     """
    #     Authorized user cannot see an attachments list of another user
    #     """
    #     pass
    #
    # def user_access_notes(self):
    #     """
    #     Unauthorized user cannot edit, any note
    #     """
    #     pass
    #
    # def user_access_labels(self):
    #     """
    #     Unauthorized user cannot see, any labels
    #     """
    #     pass
    #
    # def user_access_category(self):
    #     """
    #     Unauthorized user cannot see, any categories
    #     """
    #     pass

