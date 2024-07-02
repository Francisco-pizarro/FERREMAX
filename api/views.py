from rest_framework import generics, status
from rest_framework.views import APIView
from .models import Producto, Pago
from rest_framework.exceptions import ValidationError
from .serializers import ProductoSerializer
from rest_framework.response import Response
import requests
from .transbank_integration import iniciar_transaccion, confirmar_transaccion
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.http import Http404


def conectar_api():
    API_URL = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
    TODAY_DOLAR_VALUE_TIMESERIES_CODE = "F073.TCO.PRE.Z.D"
    GET_SERIES_FUNCTION_NAME = "GetSeries"
    params = {
        "user": 'fco.pizarro23@gmail.com',
        "pass": 'Bruno.0509',
        "timeseries": TODAY_DOLAR_VALUE_TIMESERIES_CODE,
        "function": GET_SERIES_FUNCTION_NAME,
    }
    
    api_response = requests.get(API_URL, params=params)
    api_response.raise_for_status()
    series_data = api_response.json()["Series"]["Obs"]
    last_dolar_obs = series_data[-1]
    dolar = float(last_dolar_obs["value"])
    return round(dolar, 2)

class ProductoLista(generics.ListAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    
    def list(self, request, *args, **kwargs):
        try:
            dolar = conectar_api()
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            productos_con_dolar = []
            for producto in serializer.data:
                precio_producto_dolar = round(producto['precio'] / dolar, 2)
                producto['precio_producto_dolar'] = precio_producto_dolar
                productos_con_dolar.append(producto)

            return Response(productos_con_dolar)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductoDetalle(generics.RetrieveAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            dolar = conectar_api()
            precio_producto_dolar = round(instance.precio / dolar, 2)
            data = serializer.data
            data['precio_producto_dolar'] = precio_producto_dolar
            return Response(data)
        except Producto.DoesNotExist:
            return Response({"error": "No existe el producto."}, status=status.HTTP_404_NOT_FOUND)

class ProductoDetallePorNombre(generics.RetrieveAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    lookup_field = 'nombre'

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), nombre=self.kwargs['nombre'])
        serializer = self.get_serializer(instance)
        dolar = conectar_api()
        precio_producto_dolar = round(instance.precio / dolar, 2)
        data = serializer.data
        data['precio_producto_dolar'] = precio_producto_dolar
        return Response(data)

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response({'error': 'No existe el producto.'}, status=status.HTTP_404_NOT_FOUND)
        return super().handle_exception(exc)
    
    
class ProductoCrear(generics.CreateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response(
                {"message": "Error en los datos proporcionados", "errors": e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Producto creado exitosamente", "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

# Vistas para el manejo de transacciones con Transbank
class IniciarTransaccionView(APIView):
    def get(self, request):
        return_url = request.build_absolute_uri('/api/webpay-plus/commit/')
        url, token = iniciar_transaccion(return_url)
        print(f"URL de redirección: {url}")
        print(f"Token de la transacción: {token}")
        return HttpResponseRedirect(f"{url}?token_ws={token}")

class CommitWebpayTransaction(APIView):
    def get(self, request):
        token_ws = request.query_params.get('token_ws')
        if not token_ws:
            return Response({"status": "failed", "detail": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        result = confirmar_transaccion(token_ws)
        print(f"Resultado de la confirmación de transacción: {result}")
        if result['response_code'] == 0:
            # Guardar la transacción en la base de datos
            pago = Pago(
                codigo=result['authorization_code'],
                estado=result['response_code'],
                fec_crea=timezone.now(),
                fec_update=timezone.now()
            )
            pago.save()
            
            return Response({
                "status": "success",
                "authorization_code": result['authorization_code'],
                "amount": result['amount'],
                "buy_order": result['buy_order'],
                "response_code": result['response_code'],
            })
        else:
            return Response({
                "status": "failed",
                "response_code": result['response_code'],
                "detail": result['status'],
            }, status=status.HTTP_400_BAD_REQUEST)
