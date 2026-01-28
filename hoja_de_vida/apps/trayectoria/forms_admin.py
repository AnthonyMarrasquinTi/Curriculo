"""Static admin forms for trayectoria models. Safe and non-invasive."""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import date
from .models import CursoRealizado, Reconocimiento, ExperienciaLaboral, ProductoLaboral, VentaGarage
from .validators import validate_fecha_nacimiento

ALLOWED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.webp')


class CursoRealizadoAdminForm(forms.ModelForm):
    """Static form for CursoRealizado in Django Admin."""
    certificado_subir = forms.FileField(required=False, label=_('Certificado (PDF)'))

    class Meta:
        model = CursoRealizado
        fields = '__all__'

    def clean_certificado_subir(self):
        f = self.cleaned_data.get('certificado_subir')
        if not f:
            return f
        content_type = getattr(f, 'content_type', None)
        name = getattr(f, 'name', '')
        if content_type and content_type != 'application/pdf':
            raise forms.ValidationError(_('Sólo se aceptan archivos PDF (content-type inválido).'))
        if not name.lower().endswith('.pdf'):
            raise forms.ValidationError(_('El archivo debe tener extensión .pdf'))
        return f

    def clean(self):
        cleaned = super().clean()
        fechainicio = cleaned.get('fechainicio')
        fechafin = cleaned.get('fechafin')
        # Validate ranges
        if fechainicio:
            validate_fecha_nacimiento(fechainicio)
        if fechafin:
            validate_fecha_nacimiento(fechafin)
        if fechainicio and fechafin and fechainicio > fechafin:
            raise ValidationError(_('La fecha de inicio no puede ser posterior a la fecha fin.'))
        return cleaned


class ReconocimientoAdminForm(forms.ModelForm):
    """Static form for Reconocimiento in Django Admin."""
    certificado_subir = forms.FileField(required=False, label=_('Certificado (PDF)'))

    class Meta:
        model = Reconocimiento
        fields = '__all__'

    def clean_certificado_subir(self):
        f = self.cleaned_data.get('certificado_subir')
        if not f:
            return f
        content_type = getattr(f, 'content_type', None)
        name = getattr(f, 'name', '')
        if content_type and content_type != 'application/pdf':
            raise forms.ValidationError(_('Sólo se aceptan archivos PDF (content-type inválido).'))
        if not name.lower().endswith('.pdf'):
            raise forms.ValidationError(_('El archivo debe tener extensión .pdf'))
        return f

    def clean(self):
        cleaned = super().clean()
        fechareconocimiento = cleaned.get('fechareconocimiento')
        if fechareconocimiento:
            validate_fecha_nacimiento(fechareconocimiento)
        return cleaned


class ExperienciaLaboralAdminForm(forms.ModelForm):
    class Meta:
        model = ExperienciaLaboral
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        fechainicio = cleaned.get('fechainiciogestion')
        fechafin = cleaned.get('fechafingestion')
        if fechainicio:
            validate_fecha_nacimiento(fechainicio)
        if fechafin:
            validate_fecha_nacimiento(fechafin)
        if fechainicio and fechafin and fechainicio > fechafin:
            raise ValidationError(_('La fecha de inicio no puede ser posterior a la fecha fin.'))
        return cleaned


class ProductoLaboralAdminForm(forms.ModelForm):
    class Meta:
        model = ProductoLaboral
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        fechaproducto = cleaned.get('fechaproducto')
        if fechaproducto:
            validate_fecha_nacimiento(fechaproducto)
        return cleaned


class VentaGarageAdminForm(forms.ModelForm):
    imagen_subir = forms.FileField(required=False, label=_('Imagen del Producto'))

    class Meta:
        model = VentaGarage
        fields = '__all__'

    def clean_imagen_subir(self):
        f = self.cleaned_data.get('imagen_subir')
        if not f:
            return f
        name = getattr(f, 'name', '')
        if not any(name.lower().endswith(ext) for ext in ALLOWED_IMAGE_EXTENSIONS):
            raise ValidationError(_('Tipo de imagen no permitido. Extensiones permitidas: jpg, jpeg, png, gif, webp'))
        return f

    def clean(self):
        cleaned = super().clean()
        fecha_pub = cleaned.get('fecha_publicacion')
        if fecha_pub:
            validate_fecha_nacimiento(fecha_pub)
        val = cleaned.get('valordelbien')
        if val is not None and val < 0:
            raise ValidationError(_('El valor no puede ser negativo'))
        return cleaned
