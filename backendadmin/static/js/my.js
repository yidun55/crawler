$(document).ready(
    function () {
		var startDate = new Date($("#dp4").attr("value"));
		var endDate = new Date($("#dp5").attr("value"));
		// Date picker control
		$('#dp4').datepicker()
		    .on('changeDate', function(ev){
			    if (ev.date.valueOf() > endDate.valueOf()){
				$('#alert').show().find('strong').text('The start date can not be greater then the end date');
			    } else {
				$('#alert').hide();
				startDate = new Date(ev.date);
			    }
			    $('#dp4').datepicker('hide');
			});
		$('#dp5').datepicker()
		    .on('changeDate', function(ev){
			    if (ev.date.valueOf() < startDate.valueOf()){
				$('#alert').show().find('strong').text('The end date can not be less then the start date');
			    } else {
				$('#alert').hide();
				endDate = new Date(ev.date);
			    }
			    $('#dp5').datepicker('hide');
			});

		$("#submit").click(function(event) {
			$("fm").submit();
		});
	}
);