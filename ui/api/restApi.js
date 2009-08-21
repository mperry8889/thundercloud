tc.restApi = new Object();

/* variables for REST API interaction */
tc.restApi.JobState = {
	"NEW": 0,
    "RUNNING": 1,
    "PAUSED": 2,
    "COMPLETE": 3,
};
tc.restApi._jobId = null;
tc.restApi._jobSpec = null;
tc.restApi._backend = "http://localhost:8080/api/job"
tc.restApi._state = 0;
tc.restApi._polling = false;
tc.restApi._timeoutId = 0;

/* job creation */
tc.restApi.createJobCallback = function(data, statusText) {
	tc.restApi._jobId = data;
	tc.restApi.startJob();
};
tc.restApi.createJobErrback = function(XMLHttpRequest, statusText, error) {
	tc.panel.buttons.jobStopped();
};
tc.restApi.createJob = function() {
	var jobSpec = Object();
	jobSpec.requests = {};
	for (i in tc.data.urlList._list) {
		jobSpec.requests[tc.data.urlList._list[i]] = {"method": "GET", "postdata": null, "cookies": []};
	}
	jobSpec.duration = parseInt($("#settings-duration-input").val() * $("#settings-duration-units").val());
	jobSpec.maxTransfer = parseInt($("#settings-maxTransfer-input").val() * $("#settings-maxTransfer-units").val());
	jobSpec.clientFunction = $("#settings-clientsPerSec-input").val().toString();
	jobSpec.statsGranularity = parseInt($("#settings-statsGranularity-input").val() * $("#settings-statsGranularity-units").val());
	jobSpec.profile = parseInt($("input[name=settings-profile]:checked").val());
	tc.restApi._jobSpec = jobSpec;
	$.ajax({
		type: "POST",
		url: tc.restApi._backend,
		data: $.toJSON(tc.restApi._jobSpec),
		success: tc.restApi.createJobCallback,
		error: tc.restApi.createJobErrback,
	});
};

/* start job */
tc.restApi.startJobCallback = function(data, statusText) {
	tc.restApi._state = tc.restApi.JobState.RUNNING
	tc.panel.buttons.jobRunning();
	tc.restApi.poll();
};
tc.restApi.startJobErrback = function(XMLHttpRequest, statusText, error) {
	tc.panel.buttons.jobStopped();
};
tc.restApi.startJob = function() {
	$.ajax({
		type: "POST",
		url: tc.restApi._backend + "/" + tc.restApi._jobId + "/start",
		success: tc.restApi.startJobCallback,
		error: tc.restApi.startJobErrback,
	});
};


/* stop job */
tc.restApi.stopJobCallback = function(data, statusTest) {
	if (data == "true") {
		clearTimeout(tc.restApi._timeoutId);
		tc.restApi.JobState.COMPLETE;
		tc.panel.buttons.jobStopped();
		tc.restApi.results();
	}
};
tc.restApi.stopJobErrback = function(XMLHttpRequest, statusText, error) {

};
tc.restApi.stopJob = function() {
	$.ajax({
		type: "POST",
		url: tc.restApi._backend + "/" + tc.restApi._jobId + "/stop",
		success: tc.restApi.stopJobCallback,
		error: tc.restApi.stopJobErrback,
	});
};


/* pause job */
tc.restApi.pauseJobCallback = function(data, statusTest) {
	if (data == "true") {
		clearTimeout(tc.restApi._timeoutId);
		tc.restApi._state = tc.restApi.JobState.PAUSED;
		tc.panel.buttons.jobPaused();
	}
};
tc.restApi.pauseJobErrback = function(XMLHttpRequest, statusText, error) {

};
tc.restApi.pauseJob = function() {
	$.ajax({
		type: "POST",
		url: tc.restApi._backend + "/" + tc.restApi._jobId + "/pause",
		success: tc.restApi.pauseJobCallback,
		error: tc.restApi.pauseJobErrback,
	});
};


/* resume job */
tc.restApi.resumeJobCallback = function(data, statusTest) {
	if (data == "true") {
		tc.restApi._state = tc.restApi.JobState.RUNNING;
		tc.panel.buttons.jobRunning();
		tc.restApi.poll();
	}	
};
tc.restApi.resumeJobErrback = function(XMLHttpRequest, statusText, error) {

};
tc.restApi.resumeJob = function() {
	$.ajax({
		type: "POST",
		url: tc.restApi._backend + "/" + tc.restApi._jobId + "/resume",
		success: tc.restApi.resumeJobCallback,
		error: tc.restApi.resumeJobErrback,
	});
};


/* polling code */
tc.restApi.pollCallback = function(data, statusText) {
	var response = jsonParse(data)
	tc.restApi._state = parseInt(response.state)
	$("#currentStatus").html(response.state + " " + response.elapsedTime)
	if (tc.restApi._state == tc.restApi.JobState.RUNNING) {
		tc.restApi._timeoutId = setTimeout("tc.restApi.poll()", 5000);
	}
	else if (tc.restApi._state == tc.restApi.JobState.COMPLETE) {
		tc.restApi.results();
		tc.panel.buttons.jobStopped();
	}
};
tc.restApi.pollErrback = function() {
	
};
tc.restApi.poll = function() {
	if (tc.restApi._state == tc.restApi.JobState.RUNNING) {
		$.ajax({
			type: "GET",
			url: tc.restApi._backend + "/" + tc.restApi._jobId + "/results?short=true",
			success: tc.restApi.pollCallback,
			error: tc.restApi.pollErrback,
		});
	}
};


/* stats */
tc.restApi.resultsCallback = function(data, statusText) {
	var response = jsonParse(data)
	tc.panel.results.plot(response.statisticsByTime);
};
tc.restApi.resultsErrback = function(data, statusText) {
	
};
tc.restApi.results = function() {
	$.ajax({
		type: "GET",
		url: tc.restApi._backend + "/" + tc.restApi._jobId + "/results",
		success: tc.restApi.resultsCallback,
		error: tc.restApi.resultsErrback,
	});	
};
