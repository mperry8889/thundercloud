tc.panel.results = new Object();

tc.panel.results._plot = null;

$(document).ready(function() {
	//$("#resultsGraph").css("display", "none");
	//$("#responseTimeGraph").css("display", "none");
    tc.panel.results.plot([]);
});

tc.panel.results.plot = function(data) {
	tc.panel.results.plotRequestsPerSec(data);
	tc.panel.results.plotResponseTime(data);
}
tc.panel.results.plotRequestsPerSec = function(data) {
	$("#resultsGraph").css("display", "block");

	// construct a graph-able array from the results data
	var requestsPerSec = [];
	var trendLine = [];
	var rollingAverage = 0;
	var xMax = 0;
	var yMax = 0;
	
	// JS can't access object keys like other languages, so
	// this hack is to sort the keys and then add items in order
	var keys = [];
	for (var i in data) {
		keys.push(i);
	}
	keys.sort(function(x, y) { return parseFloat(x) - parseFloat(y) });
	
	// skip 0, because nobody cares about the origin of the graph
	for (var i = 1; i < keys.length; i++) {
		var j = keys[i];
		var x = parseFloat(j);
		var y = parseFloat(data[j]["requestsPerSec"]);
		
		xMax = (x > xMax ? x : xMax);
		yMax = (y > yMax ? y : yMax);
		requestsPerSec.push([x, y]);

		newRollingAverage = ((y + ((i-1)*rollingAverage))/i)
		rollingAverage = newRollingAverage;
		trendLine.push([x, rollingAverage]);		
		
	}
	
	$.plot($("#resultsGraph"), 
        [
         { 
        	label: "requests/sec", 
        	points: { show: true }, 
        	lines: { show: true },
        	data: requestsPerSec,
         },
         {
        	label: "average",
        	points: { show: false },
        	lines: { show: true },
        	data: trendLine,
         }
        ],
        { 
        	xaxis: { max: xMax }, 
        	yaxis: { max: yMax },
        	grid: { hoverable: true, clickable: true },
        	legend: {
        		show: true,
        		position: "se",
         },
        }
	);
};
tc.panel.results.plotResponseTime = function(data) {
	$("#responseTimeGraph").css("display", "block");

	var responseTime = [];
	var xMax = 0;
	var yMax = 0;
	
	// JS can't access object keys like other languages, so
	// this hack is to sort the keys and then add items in order
	var keys = [];
	for (var i in data) {
		keys.push(i);
	}
	keys.sort(function(x, y) { return parseFloat(x) - parseFloat(y) });
	
	// skip 0, because nobody cares about the origin of the graph
	for (var i = 1; i < keys.length; i++) {
		var j = keys[i];
		var x = parseFloat(j);
		var y = parseFloat(data[j]["averageResponseTime"]*1000);
		
		xMax = (x > xMax ? x : xMax);
		yMax = (y > yMax ? y : yMax);
		responseTime.push([x, y]);
	}

	$.plot($("#responseTimeGraph"), 
        [
         { 
        	label: "average response time (ms)", 
        	points: { show: true }, 
        	lines: { show: true },
        	data: responseTime, 
         },
        ],
        { 
        	xaxis: { max: xMax }, 
        	yaxis: { max: yMax },
        	grid: { hoverable: true, clickable: true },
        	legend: {
        		show: true,
        		position: "se",
         },
        }
	);
};
