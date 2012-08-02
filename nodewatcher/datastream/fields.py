
class Field(object):
  """
  A datastream Field contains metadata on how to extract datapoints and create
  metrics from them. These metrics are then pushed via the datastream API.
  """
  def __init__(self, attribute = None):
    """
    Class constructor.

    :param attribute: Optional name of the attribute that is source of data for
      this field
    """
    self.name = None
    self.attribute = attribute

  def prepare_value(self, value):
    """
    Performs value pre-processing before inserting it into the datastream.

    :param value: Raw value extracted from the datastream object
    :return: Processed value
    """
    return value

  def prepare_tags(self):
    """
    Returns a list of tags that will be included in the final metric.
    """
    return [{ "name" : self.name }]

  def prepare_query_tags(self):
    """
    Returns a list of tags that will be used to uniquely identify the final
    metric in addition to document-specific tags. This is usually a subset
    of tags returned by `prepare_tags`.
    """
    return [{ "name" : self.name }]

  def get_downsamplers(self):
    """
    Returns a list of downsamplers that will be used for the underlying metric.
    """
    return [
      "mean",
      "sum",
      "min",
      "max",
      "sum_squares",
      "std_dev",
      "count"
    ]

  def to_stream(self, obj, stream):
    """
    Creates metrics and inserts datapoints to the stream via the datastream API.

    :param obj: Source object
    :param stream: Stream API instance
    """
    attribute = self.name if self.attribute is None else self.attribute
    value = self.prepare_value(getattr(obj, attribute))
    query_tags = obj.get_metric_query_tags() + self.prepare_query_tags()
    tags = obj.get_metric_tags() + self.prepare_tags()
    downsamplers = self.get_downsamplers()

    if hasattr(obj, "get_metric_highest_granularity"):
      highest_granularity = obj.get_metric_highest_granularity()
    else:
      highest_granularity = "seconds"

    metric_id = stream.ensure_metric(query_tags, tags, downsamplers, highest_granularity)
    stream.insert(metric_id, value)

class IntegerField(Field):
  """
  An integer-typed datastream field.
  """
  def __init__(self, **kwargs):
    """
    Class constructor.
    """
    super(IntegerField, self).__init__(**kwargs)

  def prepare_value(self, value):
    return int(value)

  def prepare_tags(self):
    return [{ "type" : "integer" }]

class FloatField(Field):
  """
  A float-typed datastream field.
  """
  def __init__(self, **kwargs):
    """
    Class constructor.
    """
    super(FloatField, self).__init__(**kwargs)

  def prepare_value(self, value):
    return float(value)

  def prepare_tags(self):
    return [{ "type" : "float" }]

class RateField(FloatField):
  """
  A rate datastream field.
  """
  def __init__(self, **kwargs):
    """
    Class constructor.
    """
    super(RateField, self).__init__(**kwargs)