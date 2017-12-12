$( function() {
  $.ui.autocomplete.prototype._renderItem = function(ul, item) {
   var newText = String(item.value).replace(
	    new RegExp(this.term, "gi"),
	    "<strong>$&</strong>");
   return $("<li></li>")
     .data("item.autocomplete", item)
     .append("<a>" + newText + "</a>")
     .appendTo(ul);
  };
  $( "#products" ).autocomplete({
    source: "/api/v1/autocomplete",
    minLength: 2,
    select: function( event, ui ) {
	$("#result").html("<a href=" + ui.item.url + ">" + ui.item.value + "</a>");
    }
  });
});
