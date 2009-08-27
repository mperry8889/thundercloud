if (tc == null) { 
	var tc = new Object();
}
if (tc.ui == null) {
	tc.ui = new Object();
}
tc.ui.dashboard = new Object();
tc.ui.dashboard.urls = [];
tc.ui.dashboard.pollInterval = 1000; // milliseconds

$(document).ready(function() {
    
    tc.ui.dashboard.progressbar = $("#dashboard-progress").progressbar({ value: 0 });  
	$("#dashboard-status").html("NEW");
	$("#dashboard-percent-complete").html("0");
	$("#dashboard-time-elapsed").html("00:00:00");
	$("#dashboard-time-remaining").html("00:00:00");
	$("#dashboard-button-pause").attr("disabled", true);
	$("#dashboard-button-stop").attr("disabled", true);
	
	$("#dashboard-button-start").click(function() {
		tc.api.startJob(tc.ui.jobId, 
						function() {
							$("#dashboard-button-pause").attr("disabled", false);
							$("#dashboard-button-stop").attr("disabled", false);
							$("#dashboard-button-start").attr("disabled", true);	
							tc.api.poll(tc.ui.jobId, tc.ui.dashboard.pollInterval, tc.ui.dashboard.update);
						},
						tc.ui.dashboard.errback
		);
	});
	$("#dashboard-button-pause").click(function() {
		switch ($("#dashboard-button-pause").val()) {
			case "Pause":
				tc.api.pauseJob(tc.ui.jobId, function() {
					$("#dashboard-button-pause").val("Resume");
					tc.api.poll(tc.ui.jobId, Infinity, tc.ui.dashboard.update);
				});
				break;
			case "Resume":
				tc.api.resumeJob(tc.ui.jobId, function() {
					$("#dashboard-button-pause").val("Pause");
					tc.api.poll(tc.ui.jobId, tc.ui.dashboard.pollInterval, tc.ui.dashboard.update);
				});
				break;
		};
	});		
	$("#dashboard-button-stop").click(function() {
		tc.api.stopJob(tc.ui.jobId, 
						function() {
							tc.ui.dashboard.jobComplete();
							tc.api.poll(tc.ui.jobId, Infinity, tc.ui.dashboard.update);
						},
						tc.ui.dashboard.errback
		);
	});	
});

tc.ui.dashboard.update = function(response) {
	var percentage = Math.min(100, 100 * (response.elapsedTime / response.duration));
	var timeleft = Math.max(0, response.duration - response.elapsedTime);
	tc.ui.dashboard.progressbar.progressbar("value", percentage);
	$("#dashboard-status").html(tc.api.JobStateToText[response.state]);
	$("#dashboard-percent-complete").html(percentage);
	$("#dashboard-time-elapsed").html(response.elapsedTime);
	$("#dashboard-time-remaining").html(timeleft);
	$("#dashboard-stats-current-iterations").html(response.iterations);
	$("#dashboard-stats-current-elapsedTime").html(response.elapsedTime);
	$("#dashboard-stats-current-bytesTransferred").html(response.bytesTransferred);
	
	if (response.state == tc.api.JobState.COMPLETE) {
		tc.ui.dashboard.jobComplete();
	}
	
};

tc.ui.dashboard.jobComplete = function() {
	$("#dashboard-button-start").attr("disabled", true);
	$("#dashboard-button-stop").attr("disabled", true);
	$("#dashboard-button-pause").attr("disabled", true);	
	tc.ui.wizard.tabs.tabs("enable", 0);
	tc.ui.newtab.reset();
};

tc.ui.dashboard.errback = function(XMLHttpRequest, statusText, error) {
	console.log(XMLHttpRequest);
	console.log(statusText);
	console.log(error);
};