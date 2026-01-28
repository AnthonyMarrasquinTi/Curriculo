from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver


class DatosPersonales(models.Model):
    idperfil = models.AutoField(primary_key=True, db_column='idperfil')
    descripcionperfil = models.CharField(max_length=50, db_column='descripcionperfil')
    perfilactivo = models.IntegerField(db_column='perfilactivo', validators=[MinValueValidator(0)])
    apellidos = models.CharField(max_length=60, db_column='apellidos')
    nombres = models.CharField(max_length=60, db_column='nombres')
    nacionalidad = models.CharField(max_length=20, db_column='nacionalidad')
    lugarnacimiento = models.CharField(max_length=60, db_column='lugarnacimiento')
    fechanacimiento = models.DateField(db_column='fechanacimiento')
    numerocedula = models.CharField(max_length=10, unique=True, db_column='numerocedula')

    SEXO_CHOICES = [
        ('H', 'H'),
        ('M', 'M'),
    ]
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, db_column='sexo')

    estadocivil = models.CharField(max_length=50, db_column='estadocivil')
    licenciaconducir = models.CharField(max_length=6, db_column='licenciaconducir')
    telefonoconvencional = models.CharField(max_length=15, db_column='telefonoconvencional')
    telefonofijo = models.CharField(max_length=15, db_column='telefonofijo')
    direcciontrabajo = models.CharField(max_length=50, db_column='direcciontrabajo')
    direcciondomiciliaria = models.CharField(max_length=50, db_column='direcciondomiciliaria')
    sitioweb = models.CharField(max_length=60, db_column='sitioweb')

    # URL segura de la foto de perfil (PNG) almacenada en Azure Blob Storage.
    foto_perfil_url = models.URLField(
        blank=True,
        null=True,
        db_column='foto_perfil_url',
        help_text='URL segura de la foto de perfil almacenada en Azure (PNG)'
    )

    class Meta:
        db_table = 'DATOSPERSONALES'

    def clean(self):
        """Validar fecha de nacimiento (entre 1981-01-01 y 2026-01-31)."""
        if self.fechanacimiento:
            earliest = date(1981, 1, 1)
            latest = date(2026, 1, 31)
            if self.fechanacimiento < earliest or self.fechanacimiento > latest:
                raise ValidationError(f'Fecha de nacimiento fuera del rango permitido ({earliest} - {latest})')


class VisibilidadSecciones(models.Model):
    """Controla qué secciones del CV se muestran en la web"""
    idvisibilidad = models.AutoField(primary_key=True, db_column='idvisibilidad')
    perfil = models.OneToOneField(DatosPersonales, on_delete=models.CASCADE, db_column='idperfil', related_name='visibilidad_secciones')
    
    mostrar_experiencia_laboral = models.BooleanField(default=True, db_column='mostrar_experiencia_laboral')
    mostrar_educacion_cursos = models.BooleanField(default=True, db_column='mostrar_educacion_cursos')
    mostrar_reconocimientos = models.BooleanField(default=True, db_column='mostrar_reconocimientos')
    mostrar_productos_academicos = models.BooleanField(default=True, db_column='mostrar_productos_academicos')
    mostrar_productos_laborales = models.BooleanField(default=True, db_column='mostrar_productos_laborales')
    mostrar_venta_garage = models.BooleanField(default=True, db_column='mostrar_venta_garage')

    class Meta:
        db_table = 'VISIBILIDADSECCIONES'
        verbose_name = 'Check Box'
        verbose_name_plural = 'Check Box'

    def __str__(self):
        return f"Visibilidad de secciones - {self.perfil.nombres} {self.perfil.apellidos}"

# Señal para crear VisibilidadSecciones automáticamente cuando se crea un DatosPersonales
@receiver(post_save, sender=DatosPersonales)
def crear_visibilidad_secciones(sender, instance, created, **kwargs):
    """Auto-crear VisibilidadSecciones para nuevos DatosPersonales"""
    if created:
        VisibilidadSecciones.objects.get_or_create(perfil=instance)