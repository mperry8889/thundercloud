tc.panel.buttons = new Object();

$(document).ready(function() {
	tc.panel.buttons.jobStopped();

	$("#control-button-start").click(function() {
		tc.restApi.createJob();
	});
	$("#control-button-stop").click(function() {
		tc.restApi.stopJob();
	});
	$("#control-button-pauseResume").click(function() {
		console.log(tc.restApi._state);
		if (tc.restApi._state == tc.restApi.JobState.RUNNING) {
			tc.restApi.pauseJob();
		}
		else {
			tc.restApi.resumeJob();
		}
	});
});

tc.panel.buttons.jobRunning = function() {
	$("#control-button-pauseResume").val("Pause");
	$("#control-button-start").attr("disabled", true);
	$("#control-button-pauseResume").attr("disabled", false);
	$("#control-button-stop").attr("disabled", false);	
};

tc.panel.buttons.jobStopped = function() {
	$("#control-button-pauseResume").val("Pause");
	$("#control-button-start").attr("disabled", false);
	$("#control-button-pauseResume").attr("disabled", true);
	$("#control-button-stop").attr("disabled", true);
};

tc.panel.buttons.jobPaused = function() {
	$("#control-button-pauseResume").val("Resume");
	$("#control-button-start").attr("disabled", true);
	$("#control-button-pauseResume").attr("disabled", false);
	$("#control-button-stop").attr("disabled", false);
};