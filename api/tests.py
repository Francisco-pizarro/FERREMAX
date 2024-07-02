from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch
from django.urls import reverse
from .views import conectar_api
from rest_framework import status
from .models import Producto
from .serializers import ProductoSerializer

#Mock prueba api valor dolar        
class ConectarApiTests(TestCase):
    @patch('api.views.requests.get')
    def test_conectar_api(self, mock_get):
        print("Iniciando la prueba de conectar_api")
        mock_response = {
            "Series": {
                "Obs": [
                    {"value": "850.25"}
                ]
            }
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
        
        # llamado Api_banco
        result = conectar_api()
        self.assertEqual(result, 850.25)

        # Verificar que requests.get fue llamado con los parámetros correctos
        API_URL = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
        params = {
            "user": 'fco.pizarro23@gmail.com',
            "pass": 'Bruno.0509',
            "timeseries": "F073.TCO.PRE.Z.D",
            "function": "GetSeries",
        }
        mock_get.assert_called_once_with(API_URL, params=params)
        
        print("Prueba Coneccion API_BANCO finalizada exitosamente")  # Mensaje de depuración

# Crear mock
class ProductoCrearMockTests(TestCase):
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
        

  #E2E DETALLE PRODUCTO NOMBRE
class ProductoDetallePorNombreTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Crear un producto de prueba en la base de datos
        self.producto = Producto.objects.create(
            nombre='ProductoTest',
            codigo='PT001',
            modelo='ModelX',
            marca='BrandY',
            stock=10,
            precio=1500
        )
  
    def test_producto_detalle_por_nombre(self):
        url = reverse('producto_detalle_por_nombre', args=[self.producto.nombre])
        response = self.client.get(url)

        # Imprime la respuesta para depuración
        print(response.status_code)
        print(response.data)

        self.assertEqual(response.status_code, 200)  # Asegura que la respuesta sea exitosa (código 200)
        self.assertEqual(response.data['nombre'], 'ProductoTest')  # Verifica que el nombre del producto coincida
        # Asegura que otros campos también coincidan según la estructura de la respuesta esperada
        self.assertEqual(response.data['codigo'], 'PT001')
        self.assertEqual(response.data['modelo'], 'ModelX')
        self.assertEqual(response.data['marca'], 'BrandY')
        self.assertEqual(response.data['stock'], 10)
        self.assertEqual(response.data['precio'], 1500)

    def Borrar_dato(self):
        self.producto.delete()
        
        

  #E2E DETALLE PRODUCTO ID        
class ProductoE2ETests(TestCase):
    
    def setUp(self):
        # Configurar datos de prueba, si es necesario
        self.client = APIClient()
        self.producto = Producto.objects.create(
            id=35,
            nombre='TEST',
            codigo='TEST',
            modelo='TEST',
            marca='TEST',
            stock=40,
            precio=5000
        )

    def test_detalle_producto_por_id(self):
        url = reverse('producto_detalle', args=[self.producto.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.producto.id)
        self.assertTrue('precio_producto_dolar' in response.data)
     
     
###Listar productos
class ProductoListaTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch('api.views.conectar_api')
    def test_producto_list(self, mock_conectar_api):
        print("Iniciando prueba de listado de productos...")
        
        # Configuración del mock
        mock_conectar_api.return_value = 800  # Simulando un valor fijo para el dólar

        # Crear productos de ejemplo
        producto1 = Producto.objects.create(nombre='Producto1', precio=1000)
        producto2 = Producto.objects.create(nombre='Producto2', precio=2000)

        url = reverse('producto_lista')  # Asegúrate de que coincida con el nombre de la ruta en urls.py

        # Realizar solicitud GET a la vista de lista de productos
        response = self.client.get(url)

        # Verificar la respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Verificar que se devuelvan los dos productos
        self.assertEqual(response.data[0]['nombre'], 'Producto1')
        self.assertEqual(response.data[1]['nombre'], 'Producto2')

        # También puedes verificar que se haya llamado a conectar_api() una vez
        mock_conectar_api.assert_called_once()

        print("Prueba de listado de productos finalizada.")

        print("Prueba de listado de productos finalizada.")