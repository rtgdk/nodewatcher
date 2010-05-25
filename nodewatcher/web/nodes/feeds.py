from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.contrib.gis.feeds import Feed as GeoFeed, W3CGeoFeed
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.conf import settings
from web.nodes.models import Event, Node, NodeType, NodeStatus
from django.contrib.sites.models import Site

class LatestEvents(Feed):
  base_link = "%s://%s" % ('https' if getattr(settings, 'FEEDS_USE_HTTPS', None) else 'http', Site.objects.get_current().domain)
  link = "%s/events/global" % base_link
  description = "Latest events generated by nodes in the network."

  def get_object(self, bits):
    if len(bits) != 1:
      return None
    
    if bits[0] == "lite":
      # I would call this a small hack
      self.description_template_name = "feeds/events_lite.html"
      return None
    else:
      return User.objects.get(id = bits[0])
  
  def title(self, obj):
    if not obj:
      return "%s - Latest network events" % settings.NETWORK_NAME

    return "%s - Latest network events for %s" % (obj.username, settings.NETWORK_NAME)
    
  def items(self, obj):
    if not obj:
      return Event.objects.order_by('-timestamp')[:30]

    return Event.objects.filter(node__owner = obj).order_by('-timestamp')[:30]

  def item_pubdate(self, item):
    return item.timestamp

  def item_guid(self, item):
    return "%s-event-%s" % (item.node.pk, item.id)
  
  def item_link(self, item):
    return "%s/nodes/events/%s" % (self.base_link, item.node.pk)

class ActiveNodes(GeoFeed):
  link = "%s://%s/" % ('https' if getattr(settings, 'FEEDS_USE_HTTPS', None) else 'http', Site.objects.get_current().domain)
  description = "Currently active nodes in the network."
  
  def title(self):
    return "%s - Active nodes" % settings.NETWORK_NAME
  
  def items(self):
    return Node.objects.filter(node_type = NodeType.Mesh).filter(status = NodeStatus.Up).exclude(geo_lat = None).exclude(geo_long = None)

  def item_pubdate(self, item):
    return item.last_seen
  
  def item_guid(self, item):
    return item.pk
  
  def item_geometry(self, item):
    return (item.geo_long, item.geo_lat)
  
  def item_link(self, item):
    return item.get_full_url()