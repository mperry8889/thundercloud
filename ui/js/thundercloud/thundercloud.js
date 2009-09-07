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
tc.api.JobStateToText = {
	0: "NEW",
	1: "RUNNING",
	2: "PAUSED",
	3: "COMPLETE",
}
tc.api.JobSpec = function() {
	this.requests = {"":{}};
	this.clientFunction = null;
	this.duration = null;
	this.statsInterval = null;
	this.transferLimit = null;
	this.profile = null;
	this.timeout = null;
}


tc.api.createJob = function(jobSpec, callback, errback) {
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job",
		data: $.toJSON(jobSpec),
		success: function(data, statusText) {
			if (callback != undefined) {
				callback(data, statusText);
			}
		},
		error: function(XMLHttpRequest, statusText, error) {
			 if (errback != undefined) {
				 errback(XMLHttpRequest, statusText, error);
			 }
		},
	});
};


tc.api.startJob = function(jobId, callback, errback) {
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job/" + jobId + "/start",
		data: {},
		success: function(data, statusText) {
			if (callback != undefined) {
				callback(data, statusText);
			}
		},
		error: function(XMLHttpRequest, statusText, error) {
			 if (errback != undefined) {
				 errback(XMLHttpRequest, statusText, error);
			 }
		},
	});
};


tc.api.pauseJob = function(jobId, callback, errback) {
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job/" + jobId + "/pause",
		data: {},
		success: function(data, statusText) {
			if (callback != undefined) {
				callback(data, statusText);
			}
		},
		error: function(XMLHttpRequest, statusText, error) {
			 if (errback != undefined) {
				 errback(XMLHttpRequest, statusText, error);
			 }
		},
	});	
};


tc.api.resumeJob = function(jobId, callback, errback) {
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job/" + jobId + "/resume",
		data: {},
		success: function(data, statusText) {
			if (callback != undefined) {
				callback(data, statusText);
			}
		},
		error: function(XMLHttpRequest, statusText, error) {
			 if (errback != undefined) {
				 errback(XMLHttpRequest, statusText, error);
			 }
		},
	});	
};


tc.api.stopJob = function(jobId, callback, errback) {
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job/" + jobId + "/stop",
		data: {},
		success: function(data, statusText) {
			if (callback != undefined) {
				callback(data, statusText);
			}
		},
		error: function(XMLHttpRequest, statusText, error) {
			 if (errback != undefined) {
				 errback(XMLHttpRequest, statusText, error);
			 }
		},
	});
};


tc.api.jobState = function(jobId, callback, errback) {
	$.ajax({
		type: "GET",
		url: tc.api.backend + "/job/" + jobId + "/state",
		success: function(data, statusText) {
			if (callback != undefined) {
				callback(data, statusText);
			}
		},
		error: function(XMLHttpRequest, statusText, error) {
			 if (errback != undefined) {
				 errback(XMLHttpRequest, statusText, error);
			 }
		},
	});
};


tc.api.jobResults = function(jobId, summaryOnly, callback, errback) { // summaryOnly == short, but short is a reserver keyword in JS
	var suffix = summaryOnly == true ? "?short=true" : "";
	$.ajax({
		type: "GET",
		url: tc.api.backend + "/job/" + jobId + "/results" + suffix,
		success: function(data, statusText) {
			if (callback != undefined) {
				callback(data, statusText);
			}
		},
		error: function(XMLHttpRequest, statusText, error) {
			 if (errback != undefined) {
				 errback(XMLHttpRequest, statusText, error);
			 }
		},
	});	
};


/* map job ID <-> polls for each job. this enforces one poll per job, and
   allows the backend here to cancel outstanding polls when jobs get updated.
   this probably breaks some kind of abstraction, but whatever */
tc.api.pollMap = {};
tc.api.poll = function(jobId, delay, callback, errback) {
	if (tc.api.pollMap[jobId]) {
		clearTimeout(tc.api.pollMap[jobId]["timeoutId"]);
	}
	tc.api.pollMap[jobId] = { delay: delay, timeoutId: null, callback: callback };
	tc.api.jobResults(jobId, true, function(data, statusText) {
		var response = jsonParse(data);
		var state = parseInt(response.state);
		var jobId = parseInt(response.jobId);
		var delay = tc.api.pollMap[jobId]["delay"];
		var callback = tc.api.pollMap[jobId]["callback"];
		var errback = null;
		if (state == tc.api.JobState.RUNNING) {
			var timeoutId = setTimeout("tc.api.poll(" + jobId + ", " + delay + ", " + callback + ", " + errback + ")", delay);
		}
		if (callback != undefined) {
			callback(response);
		}
	});
}
tc.api.cancelPoll = function(jobId) {
	if (tc.api.pollMap[jobId]) {
		clearTimeout(tc.api.pollMap[jobId]["timeoutId"]);
		tc.api.pollMap.removeAttribute(jobId);
	}
}
