function initMap() {
        var geocode = JSON.parse(document.getElementById("geocoord").dataset.geocode);

        var location = new google.maps.LatLng(geocode[0], geocode[1]);
        var mapCanvas = document.getElementById('map');
        var mapOptions = {
            center: location,
            zoom: 6,
            panControl: false,
            scrollwheel: false,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        }
        var map = new google.maps.Map(mapCanvas, mapOptions);


        var markerImage = document.getElementById("marker").dataset.marker;

        var marker = new google.maps.Marker({
            position: location,
            map: map
            });

        var styles = [{"featureType": "landscape", "stylers": [{"saturation": -100}, {"lightness": 65}, {"visibility": "on"}]}, {"featureType": "poi", "stylers": [{"saturation": -100}, {"lightness": 51}, {"visibility": "simplified"}]}, {"featureType": "road.highway", "stylers": [{"saturation": -100}, {"visibility": "simplified"}]}, {"featureType": "road.arterial", "stylers": [{"saturation": -100}, {"lightness": 30}, {"visibility": "on"}]}, {"featureType": "road.local", "stylers": [{"saturation": -100}, {"lightness": 40}, {"visibility": "on"}]}, {"featureType": "transit", "stylers": [{"saturation": -100}, {"visibility": "simplified"}]}, {"featureType": "administrative.province", "stylers": [{"visibility": "off"}]}, {"featureType": "water", "elementType": "labels", "stylers": [{"visibility": "on"}, {"lightness": -25}, {"saturation": -100}]}, {"featureType": "water", "elementType": "geometry", "stylers": [{"hue": "#ffff00"}, {"lightness": -25}, {"saturation": -97}]}];

        map.set('styles', styles);

        var contentString = '<div class="info-window">' +
                '<h3>Alert!</h3>' +
                '<div class="info-content">' +
                '<p>beacon distress location ' + geocode[0] + ' , ' + geocode[1] + '</p>' +
                '</div>' +
                '</div>';

        var infowindow = new google.maps.InfoWindow({
            content: contentString,
            maxWidth: 400
        });

        marker.addListener('click', function () {
            infowindow.open(map, marker);
        });


       
      }