"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from apps.perfil.views import hoja_vida_publica, descargar_cv_pdf, descargar_cv_completo_pdf, ver_foto_perfil, seleccionar_secciones_cv, descargar_cv_personalizado, marketplace
from apps.trayectoria.views import ver_certificado_curso, ver_certificado_reconocimiento, ver_certificado_experiencia
from apps.trayectoria.views import ver_imagen_venta_garage

urlpatterns = [
    path('', hoja_vida_publica, name='hoja_vida_publica'),
    path('descargar-cv/', descargar_cv_pdf, name='descargar_cv_pdf'),
    path('descargar-cv-completo/', descargar_cv_completo_pdf, name='descargar_cv_completo_pdf'),
    path('seleccionar-secciones/', seleccionar_secciones_cv, name='seleccionar_secciones_cv'),
    path('descargar-cv-personalizado/', descargar_cv_personalizado, name='descargar_cv_personalizado'),
    path('marketplace/', marketplace, name='marketplace'),

    # Certificate proxy endpoints
    path('certificados/curso/<int:curso_id>/', ver_certificado_curso, name='ver_certificado_curso'),
    path('certificados/reconocimiento/<int:reconocimiento_id>/', ver_certificado_reconocimiento, name='ver_certificado_reconocimiento'),
    path('certificados/experiencia/<int:experiencia_id>/', ver_certificado_experiencia, name='ver_certificado_experiencia'),

    # Venta Garage image proxy
    path('imagen-venta-garage/<int:venta_id>/', ver_imagen_venta_garage, name='ver_imagen_venta_garage'),

    # Secure profile photo endpoint
    path('foto-perfil/', ver_foto_perfil, name='ver_foto_perfil'),
    path('admin/', admin.site.urls),
]
