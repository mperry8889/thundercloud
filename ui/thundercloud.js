var tc = new Object();
tc.data = new Object();
tc.panel = new Object();
tc.restApi = new Object();

tc.data.urlList = new Object();
tc.data.urlList._list = [];
tc.data.urlList.add = function(url) {
	for (i in tc.data.urlList._list) {
		if (tc.data.urlList._list[i] == url) {
			throw "Duplicate URL";
		}
	}
	tc.data.urlList._list.push(url);
};
tc.data.urlList.del = function(url) {
	for (var i = 0; i <= tc.data.urlList._list.length; i++) {
		if (url == tc.data.urlList._list[i]) {
			tc.data.urlList._list.splice(i, 1);
			return;
		}		
	}
};
tc.data.urlList.alert = function() {
	console.log(tc.data.urlList._list);
};

tc.restApi._jobId = null;
tc.restApi._jobSpec = null;
tc.restApi._backend = "http://localhost:8080/api/job"
tc.restApi.createJobCallback = function(data, statusText) {
	tc.restApi._jobId = data;
	tc.restApi.startJob();
};
tc.restApi.createJob = function() {
	var jobSpec = Object();
	jobSpec.requests = {};
	for (i in tc.data.urlList._list) {
		jobSpec.requests[tc.data.urlList._list[i]] = {"method": "GET", "postdata": null, "cookies": []};
	}
	jobSpec.duration = 10;
	jobSpec.maxTransfer = 10240;
	jobSpec.clientFunction = "5";
	jobSpec.statsGranularity = 10;
	jobSpec.profile = 1;
	tc.restApi._jobSpec = jobSpec;
	$.post(tc.restApi._backend, $.toJSON(tc.restApi._jobSpec), tc.restApi.createJobCallback, "json");
};

tc.restApi.startJobCallback = function(data, statusText) {
	console.log("starting job");
};
tc.restApi.startJob = function() {
	$.post(tc.restApi._backend + "/" + tc.restApi._jobId + "/start", null, tc.restApi.startJobCallback);
};