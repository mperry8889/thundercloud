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


tc.api.startJob = function(jobSpec, callback, errback) {
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job",
		data: $.toJSON(jobSpec),
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



tc.api.stopJob = function(jobSpec, callback, errback) {
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job",
		data: $.toJSON(jobSpec),
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



tc.api.jobState = function(jobSpec, callback, errback) {
	$.ajax({
		type: "POST",
		url: tc.api.backend + "/job",
		data: $.toJSON(jobSpec),
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


tc.api.poll = function(jobId, callback, errback) {
	
}
tc.api.pollCallback = function(data, statusText) {
	
};
tc.api.pollErrback = function(XMLHttpRequest, statusText, error) {
	
};
