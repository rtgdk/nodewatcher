from nodewatcher.core.monitor import processors as monitor_processors
from nodewatcher.modules.monitor.sources.http import processors as http_processors

from . import models


class Koruza(monitor_processors.NodeProcessor):
    """
    Stores KORUZA monitor data into the database. Will only run if HTTP
    monitor module has previously fetched data.
    """

    @monitor_processors.depends_on_context("http", http_processors.HTTPTelemetryContext)
    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        version = context.http.get_module_version('irnas.koruza')

        if version >= 1:
            koruza = node.monitoring.irnas.koruza(create=models.KoruzaMonitor)
            status = context.http.irnas.koruza.status
            koruza.mcu_connected = bool(status.connected)
            koruza.motor_x = int(status.motors.x)
            koruza.motor_y = int(status.motors.y)
            koruza.save()

        return context
