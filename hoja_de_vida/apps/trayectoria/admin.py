from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from .models import (
    ExperienciaLaboral,
    Reconocimiento,
    CursoRealizado,
    ProductoAcademico,
    ProductoLaboral,
    VentaGarage,
)
from .forms_admin import CursoRealizadoAdminForm, ReconocimientoAdminForm, ExperienciaLaboralAdminForm, ProductoLaboralAdminForm, VentaGarageAdminForm
from .services.azure_storage import upload_pdf, upload_image
from django.core.exceptions import ValidationError


@admin.register(ExperienciaLaboral)
class ExperienciaLaboralAdmin(admin.ModelAdmin):
    form = ExperienciaLaboralAdminForm
    list_display = ('cargodesempenado', 'activarparaqueseveaenfront')

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
        except Exception as e:
            messages.error(request, str(e))
            return
        super().save_model(request, obj, form, change)


@admin.register(Reconocimiento)
class ReconocimientoAdmin(admin.ModelAdmin):
    form = ReconocimientoAdminForm
    list_display = ('descripcionreconocimiento', 'activarparaqueseveaenfront')

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
        except Exception as e:
            messages.error(request, str(e))
            return
        # If a file was uploaded, send to Azure and save URL
        uploaded = form.cleaned_data.get('certificado_subir')
        if uploaded:
            url = upload_pdf(uploaded, filename=uploaded.name)
            obj.rutacertificado = url
        super().save_model(request, obj, form, change)


@admin.register(CursoRealizado)
class CursoRealizadoAdmin(admin.ModelAdmin):
    form = CursoRealizadoAdminForm
    list_display = ('nombrecurso', 'activarparaqueseveaenfront')

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
        except Exception as e:
            messages.error(request, str(e))
            return
        uploaded = form.cleaned_data.get('certificado_subir')
        if uploaded:
            try:
                url = upload_pdf(uploaded, filename=uploaded.name)
                obj.rutacertificado = url
            except Exception as exc:
                messages.error(request, f'Error al subir a Azure: {exc}')
        super().save_model(request, obj, form, change)


@admin.register(ProductoAcademico)
class ProductoAcademicoAdmin(admin.ModelAdmin):
    list_display = ('nombrerecurso', 'activarparaqueseveaenfront')


@admin.register(ProductoLaboral)
class ProductoLaboralAdmin(admin.ModelAdmin):
    form = ProductoLaboralAdminForm
    list_display = ('nombreproducto', 'activarparaqueseveaenfront')

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
        except Exception as e:
            messages.error(request, str(e))
            return
        super().save_model(request, obj, form, change)


@admin.register(VentaGarage)
class VentaGarageAdmin(admin.ModelAdmin):
    form = VentaGarageAdminForm
    list_display = ('nombreproducto', 'fecha_publicacion', 'disponibilidad', 'activarparaqueseveaenfront')
    
    fieldsets = (
        ('Información del Producto', {
            'fields': ('idperfilconqueestaactivo', 'nombreproducto', 'estadoproducto', 'descripcion', 'valordelbien', 'rutaimagen')
        }),
        ('Publicación', {
            'fields': ('fecha_publicacion', 'disponibilidad', 'activarparaqueseveaenfront')
        }),
    )

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
        except Exception as e:
            messages.error(request, str(e))
            return

        uploaded = form.cleaned_data.get('imagen_subir')
        if uploaded:
            try:
                url = upload_image(uploaded, filename=uploaded.name)
                obj.rutaimagen = url
            except Exception as exc:
                messages.error(request, f'Error al subir imagen a Azure: {exc}')
                return

        super().save_model(request, obj, form, change)
