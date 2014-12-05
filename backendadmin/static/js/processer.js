$(document).ready(
    function() {
	// processer stats data init.
	loadDaily($("#query_date").val());
	$("#query_date").change(
	    function () {
		loadDaily(this.value);
	    }
	);

	// load groups data
        $("tbody[id=groups]").each(
	    function(index) {
		var html = "";
		var tbody = $(this);
		$.get("/process_group?groupby=" + $(this).attr("groupby"), 
		      function(data) {
			  for (var d in data) {
			      var tr = "";
			      tr += "<tr>";
			      tr += "<td>" + (Number(d) + 1).toString() + "</td>";
			      tr += "<td>" + data[d]._id + "</td>";
			      tr += "<td>" + data[d].total + "</td>";
			      tr += "</tr>";
			      html += tr;
			  }
			  tbody.html(html);
			  $("table#sort-table-" + tbody.attr("groupby")).tablesorter({ sortList: [[2,1]] });
		      }, 
		      "json");
	    }
	);

	// load total count
	$.get("/process_total", 
	      function(data) {
		  $("#info_total").text(data.info_count);
		  $("#image_total").text(data.image_count);
	      }, 
	      "json");

	// table sortable
    }
);

function loadDaily(date_str) {
    var html = "";
    $.get('/process_daily?date=' + date_str, 
	  function(data) {
	      for (var d in data) {
		  var tr = "";
		  tr += "<tr>";
		  tr += "<td>" + data[d].domain_name + "</td>";
		  tr += "<td>" + data[d].item_in + "</td>";
		  tr += "<td>" + data[d].item_ignore_duplicate + "</td>";
		  tr += "<td>" + data[d].item_ignore + "</td>";
		  tr += "<td>" + data[d].item_out_append + "</td>";
		  tr += "<td>" + data[d].item_out_update + "</td>";
		  tr += "</tr>";
		  html += tr;
	      }
	      
	      $("table#sort-table").tablesorter({ sortList: [[2,1]] });
	      $("#st_body").html(html);
	  }, 
	  "json");
}