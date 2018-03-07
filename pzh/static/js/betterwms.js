/**
 * 
 */
L.TileLayer.BetterWMS = L.TileLayer.WMS.extend({
  
  onAdd: function (map) {
    // Triggered when the layer is added to a map.
    L.TileLayer.WMS.prototype.onAdd.call(this, map);
    map.on('click', this.getFeatureInfo, this);
    if ('legend' in this.wmsParams) {
    	var legend = this.wmsParams['legend']; 
    	legend.addTo(map);
    }
  },
  
  onRemove: function (map) {
    // Triggered when the layer is removed from a map.
    L.TileLayer.WMS.prototype.onRemove.call(this, map);
    map.off('click', this.getFeatureInfo, this);
    if ('legend' in this.wmsParams) {
    	var legend = this.wmsParams['legend']; 
    	legend.remove();
    }
  },
  
  getFeatureInfo: function (evt) {
    var url = this.getFeatureInfoUrl(evt.latlng), 
    	showResults = L.Util.bind(this.showGetFeatureInfo, this);
    $.get(url, function (data) {
        var err = typeof data === 'string' ? null : data;
        showResults(err, evt.latlng, data);
      })
      .fail(function (xhr, status, error) {
        showResults("Error: "+error);  
      })
      .always(function(){});
  },
  
  getFeatureInfoUrl: function (latlng) {
    // Construct a GetFeatureInfo request URL given a point
    var point = this._map.latLngToContainerPoint(latlng, this._map.getZoom()),
        size = this._map.getSize(),
        crs = this.options.crs || this._map.options.crs,        
        params = {
          request: 'GetFeatureInfo',
          service: 'WMS',
          srs: 'EPSG:4326',
          styles: this.wmsParams.styles,
          transparent: this.wmsParams.transparent,
          version: this.wmsParams.version,      
          format: this.wmsParams.format,
          bbox: this._map.getBounds().toBBoxString(),
          height: size.y,
          width: size.x,
          layers: this.wmsParams.layers,
          query_layers: this.wmsParams.layers,
          info_format: 'text/html',
        };
    
    if ('propertyName' in this.wmsParams)
    	params['propertyName'] = this.wmsParams.propertyName;
    	
    params[params.version === '1.3.0' ? 'i' : 'x'] = point.x;
    params[params.version === '1.3.0' ? 'j' : 'y'] = point.y;
    
    return this._url + L.Util.getParamString(params, this._url, true);
    
  },
  
  showGetFeatureInfo: function (err, latlng, content) {
    if (err) {
    	console.log(err); 
    	return; 
    }
    
    if (content) {
	    // Otherwise show the content in a popup, or something.
	    L.popup({ maxWidth: 800})
	      .setLatLng(latlng)
	      .setContent(content)
	      .openOn(this._map);
    }
  }
});

L.tileLayer.betterWms = function (url, options) {
  return new L.TileLayer.BetterWMS(url, options);  
};