from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UsersAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass', 
            email='test@example.com',
            cedula='V-99999999',
            rol='ADMINISTRADOR'
        )
        self.client.force_authenticate(user=self.user)

    def test_users_list(self):
        response = self.client.get('/api/users/gestion/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login(self):
        # Desautenticamos temporalmente para simular un login normal
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/users/auth/login/', {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['rol'], 'ADMINISTRADOR')
