from django.db import models
from django.conf import settings
from django.utils import timezone

# Opciones globales
ESTADO_RESERVA_CHOICES = [
    ('confirmada', 'Confirmada'),
    ('pendiente', 'Pendiente'),
    ('cancelada', 'Cancelada'),
]

ESTADO_PAGO_CHOICES = [
    ('completado', 'Completado'),
    ('pendiente', 'Pendiente'),
]

METODO_PAGO_CHOICES = [
    ('tarjeta', 'Tarjeta'),
    ('efectivo', 'Efectivo'),
]

DISPONIBILIDAD_CHOICES = [
    ('disponible', 'Disponible'),
    ('no_disponible', 'No Disponible'),
]

# Base abstracta con auditoría y soft delete
class BaseModelAudit(models.Model):
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_creados'
    )
    modificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_modificados'
    )
    creado_en = models.DateTimeField(default=timezone.now)
    modificado_en = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    class Meta:
        abstract = True

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(activo=True)

# Modelo Habitacion
class Habitacion(BaseModelAudit):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='habitaciones_usuario'
    )
    numero = models.CharField(max_length=10, unique=True)
    tipo = models.CharField(max_length=20)
    capacidad = models.IntegerField()
    precio_por_noche = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)
    estado = models.CharField(
        max_length=15,
        choices=DISPONIBILIDAD_CHOICES,
        default='disponible'
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        self.activo = False
        self.save()

    def __str__(self):
        return f"Habitación {self.numero} - {self.tipo}"

# Modelo Cliente
class Cliente(BaseModelAudit):
    nombre_cliente = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clientes_usuario'
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        self.activo = False
        self.save()

    def __str__(self):
        return self.nombre_cliente

# Modelo Empleado
class Empleado(BaseModelAudit):
    nombre_empleado = models.CharField(max_length=100)
    cargo = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='empleados_usuario'
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        self.activo = False
        self.save()

    def __str__(self):
        return self.nombre_empleado

# Modelo Reserva
class Reserva(BaseModelAudit):
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado_reserva = models.CharField(max_length=15, choices=ESTADO_RESERVA_CHOICES)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='reservas_cliente')
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reservas_habitacion'
    )
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reservas_empleado'
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        self.activo = False
        self.save()

    def __str__(self):
        return f"Reserva {self.id} - {self.estado_reserva}"

# Modelo Pago
class Pago(BaseModelAudit):
    fecha_pago = models.DateField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=10, choices=METODO_PAGO_CHOICES)
    estado_pago = models.CharField(max_length=15, choices=ESTADO_PAGO_CHOICES)
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='pagos_reserva'
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        self.activo = False
        self.save()

    def __str__(self):
        return f"Pago {self.id} - {self.estado_pago}"

# Modelo ServicioLavanderia
class ServicioLavanderia(BaseModelAudit):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='servicios_usuario'
    )
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.SET_NULL,
        null=True,
        related_name='servicios_habitacion'
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, default='Pendiente')
    descripcion = models.TextField(max_length=255)
    precio_servicio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        self.activo = False
        self.save()

    def __str__(self):
        habit_num = self.habitacion.numero if self.habitacion else "N/A"
        return f"Servicio #{self.id} - Habitación {habit_num} - {self.estado}"

# Modelo ReservaServicio
class ReservaServicio(BaseModelAudit):
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='servicioservicio_reserva'
    )
    servicio_lavanderia = models.ForeignKey(
        ServicioLavanderia,
        on_delete=models.CASCADE,
        related_name='servicioservicio_lavanderia'
    )
    cantidad_servicios = models.IntegerField()
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        if self.servicio_lavanderia.precio_servicio is not None:
            self.precio_total = self.servicio_lavanderia.precio_servicio * self.cantidad_servicios
        else:
            self.precio_total = 0
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.activo = False
        self.save()

    def __str__(self):
        return f"ReservaServicio {self.id}"

# Modelo Reporte
class Reporte(BaseModelAudit):
    fecha_generacion = models.DateField(default=timezone.now)
    tipo_reporte = models.CharField(max_length=50)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reportes_usuario'
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        self.activo = False
        self.save()

    def __str__(self):
        return f"Reporte {self.id} - {self.tipo_reporte}"

# Modelo de auditoría de logs
class LogEntry(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='usuarios_log_entries',
    )
    modelo = models.CharField(max_length=100)
    objeto_id = models.PositiveIntegerField()
    accion = models.CharField(max_length=50)   # 'crear', 'actualizar', 'eliminar'
    timestamp = models.DateTimeField(auto_now_add=True)
    cambios = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.timestamp}: {self.modelo}({self.objeto_id}) {self.accion}"
