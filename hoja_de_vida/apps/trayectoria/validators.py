from datetime import date
from django.core.exceptions import ValidationError


def validate_fecha_nacimiento(value):
    """Valida que una fecha esté entre 1981-01-01 y 2026-01-31.

    Levanta ValidationError si está fuera del rango.
    """
    if value is None:
        return
    earliest = date(1981, 1, 1)
    latest = date(2026, 1, 31)
    if value < earliest or value > latest:
        raise ValidationError(f'La fecha debe estar entre {earliest.isoformat()} y {latest.isoformat()}')
