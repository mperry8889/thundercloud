if (tc == null) { 
	var tc = new Object();
}
tc.api = new Object();
tc.api.backend = "/api"
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
	this.statsInterval = null;
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
