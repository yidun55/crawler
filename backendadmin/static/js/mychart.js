$(document).ready(
    function () {
	// prepare jqxChart settings
	var config = function() {
	    var source = {
		type: "GET",
		datatype: "json",
		datafields: [
                    {name: 'request', type: 'int'},
                    {name: 'append', type: 'int'},
                    {name: 'updated', type: 'int'},
                    {name: 'date_str'}
                ],
		url: "/chartdata?start=" + $("#dp4").val() + "&end=" + $("#dp5").val() + "&domain=" + $("#domain-select").val()
	    };

	    var dataAdapter = new $.jqx.dataAdapter(
		source, {
		    loadComplete: function() {
			var datas = dataAdapter.records;
			console.log(JSON.stringify(datas));
		    }
		});

	    var settings = {
		title: "Request, append & update daily run statistics",
		description: "Quantity in 30 day (" + $("#domain-select").val() + ")",
		padding: { left: 5, top: 5, right: 5, bottom: 5 },
		titlePadding: { left: 90, top: 0, right: 0, bottom: 10 },
		source: dataAdapter,
		categoryAxis:
		{
                    dataField: 'date_str',
                    showGridLines: true, 
		    unitInterval: 3, 
		    axisSize: 'auto'
		},
		colorScheme: 'scheme01',
		enableAnimations: true, 
		seriesGroups:
		[
                    {
			type: 'spline',
			columnsGapPercent: 30,
			seriesGapPercent: 20,
			valueAxis:
			{
                            minValue: 0,
//                          maxValue: 50000,
//                            unitInterval: dataAdapter.records.length ,
			    formatFunction: function(value) {
				return Math.round(value);
			    },
			    axisSize: 'auto',
                            description: 'Count of one day'
			},
			series: [
                            { dataField: 'request', displayText: 'Request'},
                            { dataField: 'append', displayText: 'Append'},
                            { dataField: 'updated', displayText: 'Update'}
			]
                    }
		]
	    };
	    return settings;
	};
	
	var startDate = new Date($("#dp4").attr("value"));
	var endDate = new Date($("#dp5").attr("value"));

	$('#chartContainer').jqxChart(config());
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

	$("#fresh").click(
	    function(event) {
		event.preventDefault();
		$('#chartContainer').jqxChart(config());
	    });
    });

Date.prototype.format = function(f) {
    //%Y-%m-%d
    year = this.getFullYear();
    month = this.getMonth() + 1;
    if (month < 10) {
	month = '0' + month;
    }
    date = this.getDate() + 1;
    if (date < 10) {
	date = '0' + date;
    }
    f = f.replace("%Y", year);
    f = f.replace("%m", month);
    f = f.replace("%d", date);
    return f;
};
