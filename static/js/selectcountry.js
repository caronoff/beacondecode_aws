<script type="text/javascript">
  $( function() {
    $( "#tags" ).autocomplete({
      source: function(request, response) {
            $.getJSON("autocomplete",{
                q: request.term, // in flask, "q" will be the argument to look for using request.args
            }, function(data) {
                response(data.matching_results); // matching_results from jsonify
            });




		},
        minLength: 2,
        select: function(event, ui) {
            var country = ui.item.value
            console.log(country);
             $('input[name="country"]').val(country);},
		change: function (event, ui) {
                if(!ui.item){
                    //http://api.jqueryui.com/autocomplete/#event-change -
                    // The item selected from the menu, if any. Otherwise the property is null
                    //so clear the item for force selection
                    $("#tags").val("");
                    $("#tags").focus();
                    alert('Valid selection required');
                }
            }
	  });
  });



  </script>



  <script type=text/javascript>
  $(function() {
    $('a#calculate').bind('click',


    function() {
      $.getJSON("{{url_for('getmid')}}", {
        a: country
      }, function(data) {
        $("#id_mid").text(data.mid);
      });
      return false;
    }




    );
  });
</script>