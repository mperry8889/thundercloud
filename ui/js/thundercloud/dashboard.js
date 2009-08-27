if (tc == null) { 
	var tc = new Object();
}
if (tc.ui == null) {
	tc.ui = new Object();
}
tc.ui.dashboard = new Object();
tc.ui.dashboard.urls = [];


$(document).ready(function() {
    
    $("#dashboard-progress").progressbar({ value: 0 });  
	$("#dashboard-status").html("NEW");
	$("#dashboard-percent-complete").html("0");
	$("#dashboard-time-remaining").html("00:00:00");
	
	
});