from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from .views import (
    ProductoLista, ProductoDetalle, ProductoDetallePorNombre, ProductoCrear,
    IniciarTransaccionView, CommitWebpayTransaction
   
)

urlpatterns = [
    path('productos/', ProductoLista.as_view(), name='producto_lista'),
    path('productos/<int:id>/', ProductoDetalle.as_view(), name='producto_detalle'),
    path('productos/<str:nombre>/', ProductoDetallePorNombre.as_view(), name='producto_detalle_nombre'),
    path('productos/crear', ProductoCrear.as_view(), name='producto_crear'),
    path('webpay-plus/init/', IniciarTransaccionView.as_view(), name='iniciar_transaccion'),
    path('webpay-plus/commit/', CommitWebpayTransaction.as_view(), name='confirmar_transaccion'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('productos/<str:nombre>/', ProductoDetallePorNombre.as_view(), name='producto_detalle_por_nombre'),#URL TEST
    path('productos/<int:id>/', ProductoDetalle.as_view(), name='test_detalle_producto_por_id'),
    path('productos/', ProductoLista.as_view(), name='test_producto_list'), #TEST
]

