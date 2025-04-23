from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Habitacion, ServicioLavanderia, Reserva, LogEntry

def log_entry_for(instance, accion):
    usuario = getattr(instance, 'modificado_por', None) or getattr(instance, 'creado_por', None)
    LogEntry.objects.create(
        usuario=usuario,
        modelo=instance.__class__.__name__,
        objeto_id=instance.pk,
        accion=accion,
        cambios={}  # opcionalmente agrega detalles de cambios
    )

@receiver(post_save, sender=Habitacion)
def log_habitacion_save(sender, instance, created, **kwargs):
    log_entry_for(instance, 'crear' if created else 'actualizar')

@receiver(pre_delete, sender=Habitacion)
def log_habitacion_delete(sender, instance, **kwargs):
    log_entry_for(instance, 'eliminar')

# Repite para ServicioLavanderia y Reserva:
@receiver(post_save, sender=ServicioLavanderia)
def log_servicio_save(sender, instance, created, **kwargs):
    log_entry_for(instance, 'crear' if created else 'actualizar')

@receiver(pre_delete, sender=ServicioLavanderia)
def log_servicio_delete(sender, instance, **kwargs):
    log_entry_for(instance, 'eliminar')

@receiver(post_save, sender=Reserva)
def log_reserva_save(sender, instance, created, **kwargs):
    log_entry_for(instance, 'crear' if created else 'actualizar')

@receiver(pre_delete, sender=Reserva)
def log_reserva_delete(sender, instance, **kwargs):
    log_entry_for(instance, 'eliminar')
