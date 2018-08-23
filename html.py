# coding=utf-8
google_map = '''<!DOCTYPE html>
        <html>
          <head>
            <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
            <meta charset="utf-8">
            <title>Location</title>
            <style>
              html, body, #map-canvas {{
                height: 100%;
                width: 100%
                margin: 0px;
                padding: 0px
              }}
            </style>
            
            <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBw4IpZdm6D7ob00fF9F9TjuZ2Eeif9QtE&callback=initMap" async defer></script>
      
            <script>

  
              function initMap(){{                              
        var location = new google.maps.LatLng({},{});
        var mapCanvas = document.getElementById('map-canvas');
        var mapOptions = {{
            center: location,
            zoom: 6,
            panControl: false,
            scrollwheel: false,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        }}
        var map = new google.maps.Map(mapCanvas, mapOptions);          
        var marker = new google.maps.Marker({{
            position: location,
            map: map
            }});
              }} 
            </script>          
          </head>
          <body>
            <div id="map-canvas"></div>
          </body>
        </html> '''




blank =                 '''<!DOCTYPE html>
        <html>
       <body>

        <h1>No Map</h1>

        <p>No Map Data.</p>

        </body>
        </html> '''

