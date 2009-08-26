var tc = new Object();
tc.api = new Object();
tc.api.backend = "http://localhost:8080/api"
tc.api.JobState = {
	"NEW": 0,
    "RUNNING": 1,
    "PAUSED": 2,
    "COMPLETE": 3,
};
tc.api.JobSpec = function() {
	this.requests = {"":{}};
	this.clientFunction = null;
	this.duration = null;
	this.statsGranularity = null;
	this.maxTransfer = null;
	this.profile = null;
}

tc.api.jobId = null;
tc.api.userCallbacks = {};
tc.api.userErrbacks = {};

tc.api.state = null;

tc.api.createJob = function(jobSpec, callback, errback) {
	tc.api.userCallbacks["create"] = callback;
	tc.api.userErrbacks["create"] = errback;
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job",
		data: $.toJSON(jobSpec),
		success: tc.api.createJobCallback,
		error: tc.api.createJobErrback,
	});
};
tc.api.createJobCallback = function(data, statusText) {
	console.log("Job " + data + " created successfully");
	tc.api.jobId = parseInt(data);
	tc.api.jobState(tc.api.jobId);
	if (tc.api.userCallbacks["create"] != undefined) {
		tc.api.userCallbacks["create"](tc.api.jobId);
	}
};
tc.api.createJobErrback = function(XMLHttpRequest, statusText, error) {
	if (tc.api.userErrbacks["create"] != undefined) {
		tc.api.userErrbacks["create"]();
	}	
};


tc.api.startJob = function(jobId, callback, errback) {
	tc.api.userCallbacks["start"] = callback;
	tc.api.userErrbacks["start"] = errback;
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job/" + jobId + "/start",
		data: {},
		success: tc.api.startJobCallback,
		error: tc.api.startJobErrback,
	});	
};
tc.api.startJobCallback = function(data, statusText) {
	tc.api.jobState(tc.api.jobId);
	if (tc.api.userCallbacks["start"] != undefined) {
		tc.api.userCallbacks["start"](data);
	}
};
tc.api.startJobErrback = function(XMLHttpRequest, statusText, error) {
	tc.api.jobState(tc.api.jobId);
	if (tc.api.userErrbacks["start"] != undefined) {
		tc.api.userErrbacks["start"]();
	}	
};



tc.api.pauseJob = function(jobId, callback, errback) {
	
};
tc.api.pauseJobCallback = function(data, statusText) {
	
};
tc.api.pauseJobErrback = function(XMLHttpRequest, statusText, error) {
	
};

tc.api.resumeJob = function(jobId, callback, errback) {
	
};
tc.api.resumeJobCallback = function(data, statusText) {
	
};
tc.api.resumeJobErrback = function(XMLHttpRequest, statusText, error) {
	
};



tc.api.stopJob = function(jobId, callback, errback) {
	tc.api.userCallbacks["stop"] = callback;
	tc.api.userErrbacks["stop"] = errback;
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job/" + jobId + "/stop",
		data: {},
		success: tc.api.stopJobCallback,
		error: tc.api.stopJobErrback,
	});	
};
tc.api.stopJobCallback = function(data, statusText) {
	tc.api.jobState(tc.api.jobId);
	if (tc.api.userCallbacks["stop"] != undefined) {
		tc.api.userCallbacks["stop"](data);
	}
};
tc.api.stopJobErrback = function(XMLHttpRequest, statusText, error) {
	tc.api.jobState(tc.api.jobId);
	if (tc.api.userErrbacks["stop"] != undefined) {
		tc.api.userErrbacks["stop"]();
	}	
};



tc.api.jobState = function(jobId, callback, errback) {
	$.ajax({
		type: "GET",
		url: tc.api.backend + "/job/" + jobId + "/results",
		success: tc.restApi.resultsCallback,
		error: tc.restApi.resultsErrback,
	});		
};
tc.api.jobStateJobCallback = function(data, statusText) {
	tc.api.state = parseInt(data);
};
tc.api.jobStateJobErrback = function(XMLHttpRequest, statusText, error) {
	
};

tc.api.jobResults = function(jobId, summaryOnly, callback, errback) { // summaryOnly == short, but short is a reserver keyword in JS
	
};
tc.api.jobResultsJobCallback = function(data, statusText) {
	
};
tc.api.jobResultsJobErrback = function(XMLHttpRequest, statusText, error) {
	
};


tc.api.poll = function(jobId, callback, errback) {
	
}
tc.api.pollCallback = function(data, statusText) {
	
};
tc.api.pollErrback = function(XMLHttpRequest, statusText, error) {
	
};


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
	console.log("error");
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
		url: tc.data.backend,
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
		url: tc.data.backend + "/" + tc.restApi._jobId + "/start",
		data: {},
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
		url: tc.data.backend + "/" + tc.restApi._jobId + "/stop",
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
		url: tc.data.backend + "/" + tc.restApi._jobId + "/pause",
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
		url: tc.data.backend + "/" + tc.restApi._jobId + "/resume",
		success: tc.restApi.resumeJobCallback,
		error: tc.restApi.resumeJobErrback,
	});
};


/* polling code */
tc.restApi.pollCallback = function(data, statusText) {
	var response = jsonParse(data)
	tc.restApi._state = parseInt(response.state)
	$("#currentStatus").html(response.elapsedTime)
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
			url: tc.data.backend + "/" + tc.restApi._jobId + "/results?short=true",
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
		url: tc.data.backend + "/" + tc.restApi._jobId + "/results",
		success: tc.restApi.resultsCallback,
		error: tc.restApi.resultsErrback,
	});	
};
