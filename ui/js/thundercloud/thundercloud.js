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
	this.transferLimit = null;
	this.profile = null;
}


tc.api.createJob = function(jobSpec, callback, errback) {
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job",
		data: $.toJSON(jobSpec),
		success: function(data, statusText) {
			tc.api.createJobCallback(data, statusText);
			if (callback != undefined) {
				callback(data, statusText);
			}
		},
		error: function(XMLHttpRequest, statusText, error) {
			 tc.api.createJobErrback(XMLHttpRequest, statusText, error);
			 if (errback != undefined) {
				 errback(XMLHttpRequest, statusText, error);
			 }
		},
	});
};
tc.api.createJobCallback = function(data, statusText) {

};
tc.api.createJobErrback = function(XMLHttpRequest, statusText, error) {

};


tc.api.startJob = function(jobId, callback, errback) {
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job/" + jobId + "/start",
		data: {},
		success: function(data, statusText) {
			tc.api.startJobCallback(data, statusText);
			if (callback != undefined) {
				callback(data, statusText);
			}
		},
		error: function(XMLHttpRequest, statusText, error) {
			 tc.api.startJobErrback(XMLHttpRequest, statusText, error);
			 if (errback != undefined) {
				 errback(XMLHttpRequest, statusText, error);
			 }
		},
	});
};
tc.api.startJobCallback = function(data, statusText) {

};
tc.api.startJobErrback = function(XMLHttpRequest, statusText, error) {

};



tc.api.pauseJob = function(jobId, callback, errback) {
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job/" + jobId + "/pause",
		data: {},
		success: function(data, statusText) {
			tc.api.pauseJobCallback(data, statusText);
			if (callback != undefined) {
				callback(data, statusText);
			}
		},
		error: function(XMLHttpRequest, statusText, error) {
			 tc.api.pauseJobErrback(XMLHttpRequest, statusText, error);
			 if (errback != undefined) {
				 errback(XMLHttpRequest, statusText, error);
			 }
		},
	});	
};
tc.api.pauseJobCallback = function(data, statusText) {
	
};
tc.api.pauseJobErrback = function(XMLHttpRequest, statusText, error) {
	
};

tc.api.resumeJob = function(jobId, callback, errback) {
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job/" + jobId + "/resume",
		data: {},
		success: function(data, statusText) {
			tc.api.resumeJobCallback(data, statusText);
			if (callback != undefined) {
				callback(data, statusText);
			}
		},
		error: function(XMLHttpRequest, statusText, error) {
			 tc.api.resumeJobErrback(XMLHttpRequest, statusText, error);
			 if (errback != undefined) {
				 errback(XMLHttpRequest, statusText, error);
			 }
		},
	});	
};
tc.api.resumeJobCallback = function(data, statusText) {
	
};
tc.api.resumeJobErrback = function(XMLHttpRequest, statusText, error) {
	
};



tc.api.stopJob = function(jobId, callback, errback) {
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job/" + jobId + "/stop",
		data: {},
		success: function(data, statusText) {
			tc.api.stopJobCallback(data, statusText);
			if (callback != undefined) {
				callback(data, statusText);
			}
		},
		error: function(XMLHttpRequest, statusText, error) {
			 tc.api.stopJobErrback(XMLHttpRequest, statusText, error);
			 if (errback != undefined) {
				 errback(XMLHttpRequest, statusText, error);
			 }
		},
	});
};
tc.api.stopJobCallback = function(data, statusText) {

};
tc.api.stopJobErrback = function(XMLHttpRequest, statusText, error) {

};



tc.api.jobState = function(jobId, callback, errback) {
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job/" + jobId + "/state",
		data: {},
		success: function(data, statusText) {
			tc.api.jobStateCallback(data, statusText);
			if (callback != undefined) {
				callback(data, statusText);
			}
		},
		error: function(XMLHttpRequest, statusText, error) {
			 tc.api.jobStateErrback(XMLHttpRequest, statusText, error);
			 if (errback != undefined) {
				 errback(XMLHttpRequest, statusText, error);
			 }
		},
	});
};
tc.api.jobStateCallback = function(data, statusText) {

};
tc.api.jobStateErrback = function(XMLHttpRequest, statusText, error) {

};

tc.api.jobResults = function(jobId, summaryOnly, callback, errback) { // summaryOnly == short, but short is a reserver keyword in JS
	
};
tc.api.jobResultsCallback = function(data, statusText) {
	
};
tc.api.jobResultsErrback = function(XMLHttpRequest, statusText, error) {
	
};


/* map job ID <-> polls for each job. this enforces one poll per job, and
   allows the backend here to cancel outstanding polls when jobs get updated.
   this probably breaks some kind of abstraction, but whatever */
tc.api.pollMap = {};
tc.api.poll = function(jobId, delay, callback, errback) {
	
}
tc.api.pollCallback = function(data, statusText) {
	
};
tc.api.pollErrback = function(XMLHttpRequest, statusText, error) {
	
};
