tc.panel.buttons = new Object();

$(document).ready(function() {
	$("#control-button-start").click(function() {
		tc.restApi.createJob();
	});
});