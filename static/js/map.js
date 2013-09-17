function PointsPainter()
{
	map = new OpenLayers.Map('map');            
	map.addControl(new OpenLayers.Control.LayerSwitcher());
            
	var gphy = new OpenLayers.Layer.Google("Google Physical",{type: google.maps.MapTypeId.TERRAIN});
	var gmap = new OpenLayers.Layer.Google("Google Streets", {numZoomLevels: 20});
	var ghyb = new OpenLayers.Layer.Google("Google Hybrid",{type: google.maps.MapTypeId.HYBRID, numZoomLevels: 20});
	var gsat = new OpenLayers.Layer.Google("Google Satellite",{type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22});

	map.addLayers([gphy, gmap, ghyb, gsat]);
	map.setCenter(new OpenLayers.LonLat(0, 0),3);
			
	this.map = map;
	this.lineLayer = new OpenLayers.Layer.Vector("Line Layer"); 
	this.map.addLayer(this.lineLayer);
	this.map.addControl(new OpenLayers.Control.DrawFeature(this.lineLayer, OpenLayers.Handler.Path));
	this.paint = function(points, pointImg) {
		var markers = new OpenLayers.Layer.Markers("Lanterns"); 
		
		var size = new OpenLayers.Size(10, 10);
        var offset = new OpenLayers.Pixel(-size.w / 2, -size.h);
        var icon = new OpenLayers.Icon(
            pointImg,
            size,
            offset);

        for(var i = 0, len = points.length; i < len; i++) {
            var location = new OpenLayers.LonLat(points[i].x, points[i].y);
            markers.addMarker(new OpenLayers.Marker(location,icon.clone()));
        }
		
		this.map.addLayer(markers);
	}
	
	this.paintLine = function(start, stop, thickness)
	{
		var points = [
		   new OpenLayers.Geometry.Point(start.x, start.y),
		   new OpenLayers.Geometry.Point(stop.x, stop.y)
		];

		var line = new OpenLayers.Geometry.LineString(points);
		
		var style = { 
		  strokeColor: '#0000ff', 
		  strokeOpacity: 0.5,
		  strokeWidth: thickness,
		};

		var lineFeature = new OpenLayers.Feature.Vector(line, null, style);
		this.lineLayer.addFeatures([lineFeature]);
	}
}

PointsPainter.prototype.map = 1;
PointsPainter.prototype.lineLayer = 1;
