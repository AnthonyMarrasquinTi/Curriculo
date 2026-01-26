from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
from apps.perfil.models import DatosPersonales


class ExperienciaLaboral(models.Model):
    idexperiencilaboral = models.AutoField(primary_key=True, db_column='idexperiencilaboral')
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column='idperfilconqueestaactivo')
    cargodesempenado = models.CharField(max_length=100, db_column='cargodesempenado', null=True, blank=True)
    nombrempresa = models.CharField(max_length=50, db_column='nombrempresa', null=True, blank=True)
    lugarempresa = models.CharField(max_length=50, db_column='lugarempresa', null=True, blank=True)
    emailempresa = models.CharField(max_length=100, db_column='emailempresa', null=True, blank=True)
    sitiowebempresa = models.CharField(max_length=100, db_column='sitiowebempresa', null=True, blank=True)
    nombrecontactoempresarial = models.CharField(max_length=100, db_column='nombrecontactoempresarial', null=True, blank=True)
    telefonocontactoempresarial = models.CharField(max_length=60, db_column='telefonocontactoempresarial', null=True, blank=True)
    fechainiciogestion = models.DateField(db_column='fechainiciogestion', null=True, blank=True)
    fechafingestion = models.DateField(db_column='fechafingestion', null=True, blank=True)
    descripcionfunciones = models.CharField(max_length=100, db_column='descripcionfunciones', null=True, blank=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, db_column='activarparaqueseveaenfront')
    rutacertificado = models.CharField(max_length=100, db_column='rutacertificado', null=True, blank=True)

    class Meta:
        db_table = 'EXPERIENCIALABORAL'

    def clean(self):
        """Validar fechas de experiencia laboral."""
        if self.fechainiciogestion and self.fechafingestion:
            if self.fechainiciogestion > self.fechafingestion:
                raise ValidationError("error de fecha")
        
        if self.fechafingestion and self.fechafingestion > date(2026, 1, 31):
            raise ValidationError("error de fecha")


class Reconocimiento(models.Model):
    idreconocimiento = models.AutoField(primary_key=True, db_column='idreconocimiento')
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column='idperfilconqueestaactivo')

    TIPORECONOCIMIENTO_CHOICES = [
        ('Académico', 'Académico'),
        ('Público', 'Público'),
        ('Privado', 'Privado'),
    ]
    tiporeconocimiento = models.CharField(max_length=100, choices=TIPORECONOCIMIENTO_CHOICES, db_column='tiporeconocimiento', null=True, blank=True)
    fechareconocimiento = models.DateField(db_column='fechareconocimiento', null=True, blank=True)
    descripcionreconocimiento = models.CharField(max_length=100, db_column='descripcionreconocimiento', null=True, blank=True)
    entidadpatrocinadora = models.CharField(max_length=100, db_column='entidadpatrocinadora', null=True, blank=True)
    nombrecontactoauspicia = models.CharField(max_length=100, db_column='nombrecontactoauspicia', null=True, blank=True)
    telefonocontactoauspicia = models.CharField(max_length=60, db_column='telefonocontactoauspicia', null=True, blank=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, db_column='activarparaqueseveaenfront')
    rutacertificado = models.CharField(max_length=100, db_column='rutacertificado', null=True, blank=True)

    class Meta:
        db_table = 'RECONOCIMIENTOS'

    def clean(self):
        """Validar fecha del reconocimiento."""
        if self.fechareconocimiento and self.fechareconocimiento > date(2026, 1, 31):
            raise ValidationError("error de fecha")


class CursoRealizado(models.Model):
    idcursorealizado = models.AutoField(primary_key=True, db_column='idcursorealizado')
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column='idperfilconqueestaactivo')
    nombrecurso = models.CharField(max_length=100, db_column='nombrecurso', null=True, blank=True)
    fechainicio = models.DateField(db_column='fechainicio', null=True, blank=True)
    fechafin = models.DateField(db_column='fechafin', null=True, blank=True)
    totalhoras = models.IntegerField(db_column='totalhoras', null=True, blank=True)
    descripcioncurso = models.CharField(max_length=100, db_column='descripcioncurso', null=True, blank=True)
    entidadpatrocinadora = models.CharField(max_length=100, db_column='entidadpatrocinadora', null=True, blank=True)
    nombrecontactoauspicia = models.CharField(max_length=100, db_column='nombrecontactoauspicia', null=True, blank=True)
    telefonocontactoauspicia = models.CharField(max_length=60, db_column='telefonocontactoauspicia', null=True, blank=True)
    emailempresapatrocinadora = models.CharField(max_length=60, db_column='emailempresapatrocinadora', null=True, blank=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, db_column='activarparaqueseveaenfront')
    rutacertificado = models.CharField(max_length=100, db_column='rutacertificado', null=True, blank=True)

    class Meta:
        db_table = 'CURSOSREALIZADOS'

    def clean(self):
        """Validar fechas del curso."""
        if self.fechainicio and self.fechafin:
            if self.fechainicio > self.fechafin:
                raise ValidationError("error de fecha")
        
        if self.fechafin and self.fechafin > date(2026, 1, 31):
            raise ValidationError("error de fecha")


class ProductoAcademico(models.Model):
    idproductoacademico = models.AutoField(primary_key=True, db_column='idproductoacademico')
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column='idperfilconqueestaactivo')
    nombrerecurso = models.CharField(max_length=100, db_column='nombrerecurso', null=True, blank=True)
    clasificador = models.CharField(max_length=100, db_column='clasificador', null=True, blank=True)
    descripcion = models.CharField(max_length=100, db_column='descripcion', null=True, blank=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, db_column='activarparaqueseveaenfront')

    class Meta:
        db_table = 'PRODUCTOSACADEMICOS'


class ProductoLaboral(models.Model):
    idproductoslaborales = models.AutoField(primary_key=True, db_column='idproductoslaborales')
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column='idperfilconqueestaactivo')
    nombreproducto = models.CharField(max_length=100, db_column='nombreproducto', null=True, blank=True)
    fechaproducto = models.DateField(db_column='fechaproducto', null=True, blank=True)
    descripcion = models.CharField(max_length=100, db_column='descripcion', null=True, blank=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, db_column='activarparaqueseveaenfront')

    class Meta:
        db_table = 'PRODUCTOSLABORALES'

    def clean(self):
        """Validar fecha del producto laboral."""
        if self.fechaproducto and self.fechaproducto > date(2026, 1, 31):
            raise ValidationError("error de fecha")


class VentaGarage(models.Model):
    idventagarage = models.AutoField(primary_key=True, db_column='idventagarage')
    idperfilconqueestaactivo = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column='idperfilconqueestaactivo')
    nombreproducto = models.CharField(max_length=100, db_column='nombreproducto', null=True, blank=True)

    ESTADO_CHOICES = [
        ('Bueno', 'Bueno'),
        ('Regular', 'Regular'),
    ]
    estadoproducto = models.CharField(max_length=40, choices=ESTADO_CHOICES, db_column='estadoproducto', null=True, blank=True)
    descripcion = models.CharField(max_length=100, db_column='descripcion', null=True, blank=True)
    valordelbien = models.DecimalField(max_digits=5, decimal_places=2, db_column='valordelbien', null=True, blank=True)
    activarparaqueseveaenfront = models.BooleanField(default=True, db_column='activarparaqueseveaenfront')
    fecha_publicacion = models.DateField(db_column='fecha_publicacion', null=True, blank=True)
    
    DISPONIBILIDAD_CHOICES = [
        ('Disponible', 'Disponible'),
        ('Vendido', 'Vendido'),
    ]
    disponibilidad = models.CharField(max_length=20, choices=DISPONIBILIDAD_CHOICES, default='Disponible', db_column='disponibilidad')

    class Meta:
        db_table = 'VENTAGARAGE'

    def clean(self):
        """Validar fecha de publicación."""
        if self.fecha_publicacion and self.fecha_publicacion > date(2026, 1, 31):
            raise ValidationError("La fecha de publicación no puede ser mayor a 2026-01-31")
