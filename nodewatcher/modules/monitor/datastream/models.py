from django.utils.translation import gettext_noop

from django_datastream import datastream

# To create node.monitoring registration point
import nodewatcher.core.monitor
from nodewatcher.core.monitor import models

from . import base, fields
from .pool import pool


class RegistryItemStreams(base.StreamsBase):
    """
    Base class for registry item stream attributes.
    """

    def get_stream_query_tags(self):
        """
        Returns a set of tags that uniquely identify this object.

        :return: A dictionary of tags that uniquely identify this object
        """

        return {
            'node': self._model.root.uuid,
            'registry_id': self._model.RegistryMeta.registry_id,
        }

    def get_stream_tags(self):
        """
        Returns the stream tags that should be included in every stream
        derived from this object.

        :return: A dictionary of tags to include
        """

        return {
            'node': self._model.root.uuid,
            'registry_id': self._model.RegistryMeta.registry_id,
        }

    def get_stream_highest_granularity(self):
        """
        Returns the highest granularity that should be used by default for
        all streams derived from this object.
        """

        return datastream.Granularity.Minutes


class ProxyRegistryItemStreams(RegistryItemStreams):
    """
    A convenience class that can be used in models that reference
    registry items but are not registry items themselves.
    """

    class CombinedProxyModel(object):
        def __init__(self, *models):
            self.models = models

        def __getattr__(self, key):
            for mdl in self.models:
                try:
                    return getattr(mdl, key)
                except AttributeError:
                    continue

            raise AttributeError(key)

    def __init__(self, model):
        """
        Class constructor.
        """

        super(ProxyRegistryItemStreams, self).__init__(
            ProxyRegistryItemStreams.CombinedProxyModel(model, self.get_base(model))
        )

    def get_base(self, model):
        """
        Returns the base model that this proxy should operate on.

        :param model: Original model instance
        :return: Base model instance
        """

        return model


class SystemStatusMonitorStreams(RegistryItemStreams):
    uptime = fields.IntegerField(tags={
        'title': gettext_noop("Uptime"),
        'description': gettext_noop("Uptime of the node's system."),
        'visualization': {
            'type': 'line',
            'hidden': True,
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    reboots = fields.ResetField("#uptime", tags={
        'title': gettext_noop("Reboots"),
        'description': gettext_noop("Node reboot events."),
        'visualization': {
            'type': 'event',
            'with': {'node': fields.TagReference('node')},
        }
    })

pool.register(models.SystemStatusMonitor, SystemStatusMonitorStreams)


class GeneralResourcesMonitorStreams(RegistryItemStreams):
    loadavg_1min = fields.FloatField(tags={
        'group': 'load_average',
        'title': gettext_noop("Load average (1 min)"),
        'description': gettext_noop("1 minute load average."),
        'visualization': {
            'type': 'stack',
            'with': {'group': 'load_average', 'node': fields.TagReference('node')},
        }
    })
    loadavg_5min = fields.FloatField(tags={
        'group': 'load_average',
        'title': gettext_noop("Load average (5 min)"),
        'description': gettext_noop("5 minute load average."),
        'visualization': {
            'type': 'stack',
            'with': {'group': 'load_average', 'node': fields.TagReference('node')},
        }
    })
    loadavg_15min = fields.FloatField(tags={
        'group': 'load_average',
        'title': gettext_noop("Load average (15 min)"),
        'description': gettext_noop("15 minute load average."),
        'visualization': {
            'type': 'stack',
            'with': {'group': 'load_average', 'node': fields.TagReference('node')},
        }
    })
    memory_free = fields.IntegerField(tags={
        'group': 'memory',
        'title': gettext_noop("Free memory"),
        'description': gettext_noop("Amount of free memory."),
        'visualization': {
            'type': 'stack',
            'with': {'group': 'memory', 'node': fields.TagReference('node')},
        }
    })
    memory_buffers = fields.IntegerField(tags={
        'group': 'memory',
        'title': gettext_noop("Buffers memory"),
        'description': gettext_noop("Amount of memory used for kernel buffers."),
        'visualization': {
            'type': 'stack',
            'with': {'group': 'memory', 'node': fields.TagReference('node')},
        }
    })
    memory_cache = fields.IntegerField(tags={
        'group': 'memory',
        'title': gettext_noop("Cache memory"),
        'description': gettext_noop("Amount of memory used for cache."),
        'visualization': {
            'type': 'stack',
            'with': {'group': 'memory', 'node': fields.TagReference('node')},
        }
    })
    processes = fields.IntegerField(tags={
        'title': gettext_noop("Processes"),
        'description': gettext_noop("Number of running processes."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })

pool.register(models.GeneralResourcesMonitor, GeneralResourcesMonitorStreams)


class NetworkResourcesMonitorStreams(RegistryItemStreams):
    routes = fields.IntegerField(tags={
        'title': gettext_noop("Routes"),
        'description': gettext_noop("Number of routes installed in the kernel routing tables."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    tcp_connections = fields.IntegerField(tags={
        'title': gettext_noop("TCP connections"),
        'description': gettext_noop("Number of tracked TCP connections."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    udp_connections = fields.IntegerField(tags={
        'title': gettext_noop("UDP connections"),
        'description': gettext_noop("Number of tracked UDP connections."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })


class InterfaceStreams(RegistryItemStreams):
    def get_stream_query_tags(self):
        """
        Returns a set of tags that uniquely identify this object.

        :return: A dictionary of tags that uniquely identify this object
        """

        tags = super(InterfaceStreams, self).get_stream_query_tags()
        tags.update({'interface': self._model.name})
        return tags

    def get_stream_tags(self):
        """
        Returns the stream tags that should be included in every stream
        derived from this object.

        :return: A dictionary of tags to include
        """

        tags = super(InterfaceStreams, self).get_stream_tags()
        tags.update({'interface': self._model.name})
        return tags


class InterfaceMonitorStreams(InterfaceStreams):
    tx_packets = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("TX packets (%(interface)s)")),
        'description': gettext_noop("Number of transmitted packets."),
        'visualization': {
            'hidden': True,
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    tx_packets_rate = fields.RateField("system.status#reboots", "#tx_packets", tags={
        'group': 'packets_rate',
        'title': fields.TagReference('interface', gettext_noop("TX packets rate (%(interface)s)")),
        'description': gettext_noop("Rate of transmitted packets."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'with': {
                'group': 'packets_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        }
    })
    rx_packets = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("RX packets (%(interface)s)")),
        'description': gettext_noop("Number of received packets."),
        'visualization': {
            'hidden': True,
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    rx_packets_rate = fields.RateField("system.status#reboots", "#rx_packets", tags={
        'group': 'packets_rate',
        'title': fields.TagReference('interface', gettext_noop("RX packets rate (%(interface)s)")),
        'description': gettext_noop("Rate of received packets."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'with': {
                'group': 'packets_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        }
    })
    tx_bytes = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("TX bytes (%(interface)s)")),
        'description': gettext_noop("Size of transmitted packets."),
        'visualization': {
            'hidden': True,
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    tx_bytes_rate = fields.RateField("system.status#reboots", "#tx_bytes", tags={
        'group': 'bytes_rate',
        'title': fields.TagReference('interface', gettext_noop("TX bytes rate (%(interface)s)")),
        'description': gettext_noop("Throughput of transmitted packets."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'with': {
                'group': 'bytes_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        }
    })
    rx_bytes = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("RX bytes (%(interface)s)")),
        'description': gettext_noop("Size of received packets."),
        'visualization': {
            'hidden': True,
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    rx_bytes_rate = fields.RateField("system.status#reboots", "#rx_bytes", tags={
        'group': 'bytes_rate',
        'title': fields.TagReference('interface', gettext_noop("RX bytes rate (%(interface)s)")),
        'description': gettext_noop("Throughput of received packets."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'with': {
                'group': 'bytes_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        }
    })
    tx_errors = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("TX errors (%(interface)s)")),
        'description': gettext_noop("Number of transmission errors."),
        'visualization': {
            'hidden': True,
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    tx_errors_rate = fields.RateField("system.status#reboots", "#tx_errors", tags={
        'group': 'errors_rate',
        'title': fields.TagReference('interface', gettext_noop("TX errors rate (%(interface)s)")),
        'description': gettext_noop("Rate of transmission errors."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'with': {
                'group': 'errors_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        }
    })
    rx_errors = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("RX errors (%(interface)s)")),
        'description': gettext_noop("Number of receive errors."),
        'visualization': {
            'hidden': True,
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    rx_errors_rate = fields.RateField("system.status#reboots", "#rx_errors", tags={
        'group': 'errors_rate',
        'title': fields.TagReference('interface', gettext_noop("RX errors rate (%(interface)s)")),
        'description': gettext_noop("Rate of receive errors."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'with': {
                'group': 'errors_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        }
    })
    tx_drops = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("TX drops (%(interface)s)")),
        'description': gettext_noop("Number of dropped packets when transmitting."),
        'visualization': {
            'hidden': True,
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    tx_drops_rate = fields.RateField("system.status#reboots", "#tx_drops", tags={
        'group': 'drops_rate',
        'title': fields.TagReference('interface', gettext_noop("TX drops rate (%(interface)s)")),
        'description': gettext_noop("Rate of transmission drops."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'with': {
                'group': 'drops_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        }
    })
    rx_drops = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("RX drops (%(interface)s)")),
        'description': gettext_noop("Number of dropped packets when receiving."),
        'visualization': {
            'hidden': True,
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    rx_drops_rate = fields.RateField("system.status#reboots", "#rx_drops", tags={
        'group': 'drops_rate',
        'title': fields.TagReference('interface', gettext_noop("RX drops rate (%(interface)s)")),
        'description': gettext_noop("Rate of receive errors."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
            'with': {
                'group': 'drops_rate',
                'interface': fields.TagReference('interface'),
                'node': fields.TagReference('node'),
            },
        }
    })
    mtu = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("MTU (%(interface)s)")),
        'description': gettext_noop("Interface MTU (Maximum Transmission Unit)."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })

pool.register(models.InterfaceMonitor, InterfaceMonitorStreams)


class WifiInterfaceMonitorStreams(InterfaceMonitorStreams):
    channel = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("Channel (%(interface)s)")),
        'description': gettext_noop("Channel the wireless radio is operating on."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    channel_width = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("Channel width (%(interface)s)")),
        'description': gettext_noop("Width of the channel the wireless radio is operating on."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    bitrate = fields.FloatField(tags={
        'title': fields.TagReference('interface', gettext_noop("Bitrate (%(interface)s)")),
        'description': gettext_noop("Wireless radio bitrate."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    rts_threshold = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("RTS threshold (%(interface)s)")),
        'description': gettext_noop("RTS threshold."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    frag_threshold = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("Fragmentation threshold (%(interface)s)")),
        'description': gettext_noop("Fragmentation threshold."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    signal = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("Signal (%(interface)s)")),
        'description': gettext_noop("Amount of signal in dBm."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    noise = fields.IntegerField(tags={
        'title': fields.TagReference('interface', gettext_noop("Noise (%(interface)s)")),
        'description': gettext_noop("Amount of noise in dBm."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })
    snr = fields.FloatField(tags={
        'title': fields.TagReference('interface', gettext_noop("Signal-to-noise ratio (%(interface)s)")),
        'description': gettext_noop("Signal-to-noise ratio."),
        'visualization': {
            'type': 'line',
            'time_downsamplers': ['mean'],
            'value_downsamplers': ['min', 'mean', 'max'],
        }
    })

pool.register(models.WifiInterfaceMonitor, WifiInterfaceMonitorStreams)
