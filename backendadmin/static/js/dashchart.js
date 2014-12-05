$(document).ready(
    function () {
	var config = function(start, end, domain) {
	    var source = {
		type: "GET",
		datatype: "json",
		datafields: [
                    {name: 'request', type: 'int'},
                    {name: 'append', type: 'int'},
                    {name: 'updated', type: 'int'},
                    {name: 'date_str'}
                ],
		url: "/chartdata?start=" + start + "&end=" + end + "&domain=" + domain
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
		description: "Quantity in 7 day (" + domain + ")",
		padding: { left: 5, top: 5, right: 5, bottom: 5 },
		titlePadding: { left: 90, top: 0, right: 0, bottom: 10 },
		source: dataAdapter,
		categoryAxis:
		{
                    dataField: 'date_str',
                    showGridLines: false, 
		    unitInterval: 1, 
		    axisSize: 'auto'
		},
		colorScheme: 'scheme05',
		enableAnimations: true, 
		seriesGroups:
		[
                    {
			type: 'spline',
			columnsGapPercent: 30,
			seriesGapPercent: 0,
			valueAxis:
			{
                            minValue: 0,
			    maxValue: 50000,
                            unitInterval: 10000,
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
	
	var endDate = new Date();
	var startDate = new Date(new Date() - 7 * 24 * 60 * 60 * 1000);	

	// draw the chart in every DIV which id is 'chartContainer'.
	$("div[id=chartContainer]").each(
	    function() {
		$(this).jqxChart(
		    config(startDate.format("%Y%m%d"), 
			   endDate.format("%Y%m%d"), 
			   $(this).attr("domain"))
		);
	    }
	);
    }
);

Date.prototype.format = function(f) {
    // %Y-%m-%d
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
