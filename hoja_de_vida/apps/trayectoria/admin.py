from django import forms
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
from .services.azure_storage import upload_pdf


class CertificadoUploadForm(forms.ModelForm):
    certificado_subir = forms.FileField(required=False, label=_('Certificado (PDF)'))

    class Meta:
        model = None  # will be set dynamically in ModelAdmin
        fields = '__all__'

    def clean_certificado_subir(self):
        f = self.cleaned_data.get('certificado_subir')
        if not f:
            return f
        # Validate content_type if available
        content_type = getattr(f, 'content_type', None)
        name = getattr(f, 'name', '')
        if content_type and content_type != 'application/pdf':
            raise forms.ValidationError(_('Sólo se aceptan archivos PDF (content-type inválido).'))
        if not name.lower().endswith('.pdf'):
            raise forms.ValidationError(_('El archivo debe tener extensión .pdf'))
        return f


@admin.register(ExperienciaLaboral)
class ExperienciaLaboralAdmin(admin.ModelAdmin):
    list_display = ('cargodesempenado', 'activarparaqueseveaenfront')


@admin.register(Reconocimiento)
class ReconocimientoAdmin(admin.ModelAdmin):
    list_display = ('descripcionreconocimiento', 'activarparaqueseveaenfront')

    def get_form(self, request, obj=None, **kwargs):
        # attach the model to the dynamic form
        form = type('DynamicReconocimientoForm', (CertificadoUploadForm,), {})
        form.Meta.model = Reconocimiento
        return form

    def save_model(self, request, obj, form, change):
        # If a file was uploaded, send to Azure and save URL
        uploaded = form.cleaned_data.get('certificado_subir')
        if uploaded:
            url = upload_pdf(uploaded, filename=uploaded.name)
            obj.rutacertificado = url
        super().save_model(request, obj, form, change)


@admin.register(CursoRealizado)
class CursoRealizadoAdmin(admin.ModelAdmin):
    list_display = ('nombrecurso', 'activarparaqueseveaenfront')

    def get_form(self, request, obj=None, **kwargs):
        form = type('DynamicCursoForm', (CertificadoUploadForm,), {})
        form.Meta.model = CursoRealizado
        return form

    def save_model(self, request, obj, form, change):
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
    list_display = ('nombreproducto', 'activarparaqueseveaenfront')


@admin.register(VentaGarage)
class VentaGarageAdmin(admin.ModelAdmin):
    list_display = ('nombreproducto', 'activarparaqueseveaenfront')
    # No custom forms or inline configurations yet.
