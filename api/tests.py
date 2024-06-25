from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch
from django.urls import reverse
from .models import Producto

class ProductoCrearTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('api.models.Producto.save', autospec=True)
    def test_producto_crear(self, mock_save):
        data = {
            "nombre": "Nuevo",
            "precio": 1500,
            "codigo": "NP001",
            "modelo": "ModelX",
            "marca": "BrandY",
            "stock": 5
        }
        response = self.client.post(reverse('producto_crear'), data, format='json')
        
        # Imprime la respuesta para depuración
        print(response.status_code)
        print(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Producto creado exitosamente')
        self.assertEqual(response.data['data']['nombre'], 'Nuevo')
        self.assertEqual(response.data['data']['precio'], 1500)
        self.assertEqual(response.data['data']['codigo'], 'NP001')
        self.assertEqual(response.data['data']['modelo'], 'ModelX')
        self.assertEqual(response.data['data']['marca'], 'BrandY')
        self.assertEqual(response.data['data']['stock'], 5)
        
        # Verifica que save fue llamado una vez
        self.assertTrue(mock_save.called)
        self.assertEqual(mock_save.call_count, 1)
