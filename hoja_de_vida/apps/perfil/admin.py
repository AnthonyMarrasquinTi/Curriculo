from django.contrib import admin, messages
from django import forms
from django.core.exceptions import ValidationError
from .models import DatosPersonales, VisibilidadSecciones

from apps.documentos.services.azure_storage import upload_profile_image


class DatosPersonalesAdminForm(forms.ModelForm):
    # transient upload field shown in admin only
    foto_perfil_file = forms.FileField(required=False, help_text='Subir una imagen PNG (se almacenará en Azure)')

    class Meta:
        model = DatosPersonales
        fields = '__all__'

    def clean_foto_perfil_file(self):
        f = self.cleaned_data.get('foto_perfil_file')
        if f:
            name = getattr(f, 'name', '')
            if not name.lower().endswith('.png'):
                raise ValidationError('Solo se permiten imágenes PNG (.png)')
            # If content_type is available, also check it
            content_type = getattr(f, 'content_type', '')
            if content_type and content_type != 'image/png':
                raise ValidationError('Solo se permiten imágenes PNG (content-type debe ser image/png)')
        return f


@admin.register(DatosPersonales)
class DatosPersonalesAdmin(admin.ModelAdmin):
    form = DatosPersonalesAdminForm
    list_display = ('apellidos', 'nombres', 'numerocedula', 'perfilactivo')

    fieldsets = (
        ('Información Personal', {
            'fields': ('nombres', 'apellidos', 'descripcionperfil', 'numerocedula', 'sexo', 'estadocivil', 'perfilactivo')
        }),
        ('Datos de Nacimiento', {
            'fields': ('fechanacimiento', 'nacionalidad', 'lugarnacimiento', 'licenciaconducir')
        }),
        ('Contacto', {
            'fields': ('telefonofijo', 'telefonoconvencional', 'sitioweb', 'direcciondomiciliaria', 'direcciontrabajo')
        }),
        ('Foto de Perfil', {
            'fields': ('foto_perfil_file',),
            'description': 'Sube una imagen PNG para tu perfil (se almacenará en Azure)'
        }),
    )

    class Media:
        css = {
            'all': ('perfil/css/cyberadmin.css',)
        }
        js = ('perfil/js/cyberadmin.js',)

    def save_model(self, request, obj, form, change):
        # Validar fechas
        try:
            obj.full_clean()
        except ValidationError as e:
            messages.error(request, str(e))
            return
        
        # If a PNG was uploaded via the admin form, upload to Azure and store URL
        f = form.cleaned_data.get('foto_perfil_file') if hasattr(form, 'cleaned_data') else None
        if f:
            try:
                url = upload_profile_image(f)
                obj.foto_perfil_url = url
            except Exception as exc:
                # Raise ValidationError so admin shows the problem
                raise ValidationError(f'Error subiendo la imagen a Azure: {exc}')

        super().save_model(request, obj, form, change)


@admin.register(VisibilidadSecciones)
class VisibilidadSeccionesAdmin(admin.ModelAdmin):
    list_display = ('perfil',)
    
    fieldsets = (
        ('Perfil Asociado', {
            'fields': ('perfil',)
        }),
        ('Checkboxes', {
            'fields': (
                'mostrar_experiencia_laboral',
                'mostrar_educacion_cursos',
                'mostrar_reconocimientos',
                'mostrar_productos_academicos',
                'mostrar_productos_laborales',
                'mostrar_venta_garage'
            ),
            'description': 'Marca las secciones que deseas mostrar en tu CV'
        }),
    )


# Global admin branding
admin.site.site_header = "CYBERADMIN — Panel"
admin.site.site_title = "CYBERADMIN"
admin.site.index_title = "Dashboard"
