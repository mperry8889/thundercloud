tc.panel.results = new Object();

tc.panel.results._plot = null;

$(document).ready(function() {
	$("#resultsGraph").css("display", "none");
});

tc.panel.results.plot = function(data) {
	$("#resultsGraph").css("display", "block");


	// construct a graph-able array from the results data
	var displayData = [];
	var xMax = 0;
	var yMax = 0;
	
	// JS can't access object keys like other languages, so
	// this hack is to sort the keys and then add items in order
	var keys = [];
	for (var i in data) {
		keys.push(i);
	}
	keys.sort(function(x, y) { return parseFloat(x) - parseFloat(y) });
	
	for (var i = 0; i < keys.length; i++) {
		var j = keys[i];
		var x = parseFloat(j);
		var y = parseFloat(data[j]["requestsPerSec"]);
		
		xMax = (x > xMax ? x : xMax);
		yMax = (y > yMax ? y : yMax);
		displayData.push([x, y]);
	}
	
	tc.panel.results._plot = $.plot($("#resultsGraph"), [displayData], { xaxis: { max: xMax+1 }, yaxis: { max: yMax+1 } });
};