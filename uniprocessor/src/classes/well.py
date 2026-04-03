class Well:
    """Represents a single well within a Sensor, containing data for its associated InkChannels.
    
    Attributes:
        well_id (str):                        Unique identifier for the well.
        spot_type (str):                      Spot type.
        ink_channels (Dict[str, InkChannel]): Dictionary of InkChannel objects keyed by ink channel.
    """
    def __init__(self, 
                 well_id,
                 spot_type): 
        self.well_id              = well_id
        self.spot_type            = spot_type
        self.ink_channels         = {}
        
    def __repr__(self):
        return f"Well ID: {self.well_id}, Ink Channels: {self.ink_channels}"