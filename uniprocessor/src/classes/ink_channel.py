class InkChannel:
    """Represents a single ink channel within a Well.
    
    Attributes:
        ink_channel_id (str):               Unique identifier for the ink channel.
        diff_perc_val (float):              The diff_perc value associated with the ink channel.
        corrected_incubation_val (float):   The corrected incubation value for the ink channel.
        well_performance_res (str):         Performance result at the well level.
        sensor_uniformity_val (float):      Uniformity value at the sensor level.
        sensor_uniformity_res (str):        Uniformity result at the sensor level.
        sensor_mean_val (float):            Mean value across the sensor for this ink channel.
        sensor_center4_mean_val (float):    Mean value at the center 4 positions of the sensor for this ink channel.
    """
    def __init__(self, ink_channel_id, diff_perc_val = None, cor_inc_val = None):
        self.ink_channel_id = ink_channel_id
        self._diff_perc_val = diff_perc_val
        self._corrected_incubation_val = cor_inc_val
        
        self._well_performance_res = None
        
        self._sensor_uniformity_val = None
        self._sensor_uniformity_res = None
        self._sensor_mean_val = None  # Added to store mean value across sensor
        self._sensor_center4_mean_val = None  # Add this line
        
    def __repr__(self):
        return f"Ink Channel ID: {self.ink_channel_id}, Diff Perc Value: {self.diff_perc_val}, Corrected Incubation Value: {self.corrected_incubation_val}"
    
    @property
    def diff_perc_val(self):
        return self._diff_perc_val
    @diff_perc_val.setter
    def diff_perc_val(self, value):
        self._diff_perc_val = value
    
    @property
    def corrected_incubation_val(self):
        return self._corrected_incubation_val
    @corrected_incubation_val.setter
    def corrected_incubation_val(self, value):
        self._corrected_incubation_val = value
    
    @property
    def well_performance_res(self):
        return self._well_performance_res
    @well_performance_res.setter
    def well_performance_res(self, value):
        self._well_performance_res = value
    
    @property
    def sensor_uniformity_val(self):
        return self._sensor_uniformity_val
    @sensor_uniformity_val.setter
    def sensor_uniformity_val(self, value):
        self._sensor_uniformity_val = value
    
    @property
    def sensor_uniformity_res(self):
        return self._sensor_uniformity_res
    @sensor_uniformity_res.setter
    def sensor_uniformity_res(self, value):
        self._sensor_uniformity_res = value
    
    @property
    def sensor_mean_val(self):
        return self._sensor_mean_val
    @sensor_mean_val.setter
    def sensor_mean_val(self, value):
        self._sensor_mean_val = value
    
    @property
    def sensor_center4_mean_val(self):
        return self._sensor_center4_mean_val
    @sensor_center4_mean_val.setter
    def sensor_center4_mean_val(self, value):
        self._sensor_center4_mean_val = value