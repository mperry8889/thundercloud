if (tc == null) { 
	var tc = new Object();
}
if (tc.ui == null) {
	tc.ui = new Object();
}
tc.ui.newtab = new Object();

$(document).ready(function() {
	tc.ui.newtab.reset();
});

tc.ui.newtab.reset = function() {

	$("*[id^=wizard]").unbind();
	$("*[name^=wizard]").unbind();
	$("*[id^=jobspec]").unbind();
	$("*[name^=jobspec]").unbind();
	

	tc.ui.newtab.urls = [];
	tc.ui.newtab.profile = 0;	

	tc.ui.newtab.clearUrl();
	tc.ui.newtab.clearError();
	
	$("#jobspec-duration-input").val("");
	$("#jobspec-transferLimit-input").val("");	
	tc.ui.newtab.statsSlider = $("#jobspec-statsInterval").slider({
		value: 30,
		min: 1,
		max: 120,
		step: 1,
		slide: function(event, ui) {
			$("#jobspec-statsInterval-amount").html(ui.value + " seconds");
		}
	});  
	$("#jobspec-statsInterval-amount").html(tc.ui.newtab.statsSlider.slider("value") + " seconds");           

	tc.ui.newtab.url_table = $("#jobspec-url-list").dataTable({
		"bPaginate": false,	
		"bInfo": false,
		"bSort": false,
		"bFilter": false,
		"oLanguage": {
			"sZeroRecords": "No URLs added",
		},
	});
	
	tc.ui.newtab.review_table = $("#wizard-confirm-parameters").dataTable({
		"bPaginate": false,	
		"bInfo": false,
		"bSort": false,
		"bFilter": false,
		"oLanguage": {
			"sZeroRecords": "",
		},		
	});
	
    $("#jobspec-request-url-add").click(function() {
    	try {
    		tc.ui.newtab.addUrl($("#jobspec-request-url-input").val());
    	}
    	catch (e) {
    		tc.ui.newtab.error(e);
    	}
    });
    $("#jobspec-request-url-clear").click(function() {
    	tc.ui.newtab.clearUrl();
    });
    
    
    /* JOB SETUP */
 	var wizard_tabs = $("#wizard-workflow").tabs({
 		disabled: [1,2,3],
 		select: function(event, ui) {
 			// review & confirm tab. have to use numerical index
 			if (ui.index == 3) {
 				tc.ui.newtab.reviewParameters();
 			}
 		},
 	});
 	wizard_tabs.tabs("select", 0);
 	
	$(":input[name='jobspec-profile-input']").click(function() {
		switch ($(":input[@name='jobspec-profile-input']:checked").val()) {
			case "stress":
				$("#wizard-concurrency").html("Requests/sec");
				$("#wizard-concurrency-help").html("how many requests/sec");
				tc.ui.newtab.profile = 0;
				tc.ui.newtab.resetClientFunction();
				break;
			case "benchmark":
				$("#wizard-concurrency").html("Concurrent clients");
				$("#wizard-concurrency-help").html("how many clients");
				tc.ui.newtab.profile = 1;
				tc.ui.newtab.resetClientFunction();
				break;
			case "simulation":
				$("#wizard-concurrency").html("Starting clients");
				$("#wizard-concurrency-help").html("how many clients to start");
				tc.ui.newtab.profile = 0;
				$("#wizard-function").show();
				break;
			default:
		}				
		wizard_tabs.tabs("enable", 1);
		wizard_tabs.tabs("enable", 2);
		wizard_tabs.tabs("enable", 3);
	});
	tc.ui.newtab.resetClientFunction();
	
	
	/* JOB CREATION */
	$("#wizard-create-job-link").click(function() {
		jobSpec = tc.ui.newtab.createJobSpec();
		if (tc.ui.newtab.validate(jobSpec)) {
			tc.api.createJob(jobSpec, function(jobId) {
				tc.ui.wizard.tabs.tabs("enable", 2);
				tc.ui.wizard.tabs.tabs("select", 2);
				tc.ui.wizard.tabs.tabs("disable", 0);
				tc.ui.jobId = jobId;
			});
		}
		return true;
	});	
	
	$("#wizard-clear-all-link").click(function() {
		tc.ui.newtab.reset();
	});
	
};

tc.ui.newtab.activateUrlRowClicks = function() {
	$(".jobspec-url-list-remove").click(function() {
		var rowIndex = tc.ui.newtab.url_table.fnGetPosition($(this).parent()[0])[0];
		var url = tc.ui.newtab.url_table.fnGetData(rowIndex)[0];
		tc.ui.newtab.url_table.fnDeleteRow(rowIndex);

		for (var i = 0; i <= tc.ui.newtab.urls.length; i++) {
			if (url == tc.ui.newtab.urls[i]) {
				tc.ui.newtab.urls.splice(i, 1);
				return;
			}		
		}
	});
};

tc.ui.newtab.addUrl = function(url) {
	for (var i in tc.ui.newtab.urls) {
		if (url == tc.ui.newtab.urls[i]) {
			throw "Duplicate URL";
		}
	}
	tc.ui.newtab.urls.push(url);
    tc.ui.newtab.url_table.fnAddData([url, '<a href="javascript:;" class="jobspec-url-list-remove">Remove</a>']);
    tc.ui.newtab.activateUrlRowClicks();
    tc.ui.newtab.clearUrl();
}

tc.ui.newtab.clearUrl = function() {
	$("#jobspec-request-url-input").val("");
	tc.ui.newtab.clearError();
};

tc.ui.newtab.error = function(errmsg) {
	$("#jobspec-request-url-error").html(errmsg);
	$("#jobspec-request-url-error").show("normal");
};
tc.ui.newtab.clearError = function() {
	$("#jobspec-request-url-error").hide("normal");
	$("#jobspec-request-url-error").html("");
};

tc.ui.newtab.resetClientFunction = function() {
	$("#jobspec-clients-input").val("");
	$(":input[name='jobspec-clientFunction-input']").attr("checked", false);
	$(":input[name='jobspec-clientFunction-input']").each(function() {
		if ($(this).val() == "0") {
			$(this).attr("checked", true);
			return;
		}
	});
	$("#wizard-function").hide();	
};

tc.ui.newtab.createJobSpec = function() {
	jobSpec = new tc.api.JobSpec();
	jobSpec.profile = tc.ui.newtab.profile;
	jobSpec.duration = parseInt($("#jobspec-duration-input").val() * $("#jobspec-duration-multiplier").val());
	jobSpec.transferLimit = parseInt($("#jobspec-transferLimit-input").val() * $("#jobspec-transferLimit-multiplier").val());
	jobSpec.clientFunction = $(":input[name='jobspec-clientFunction-input']:checked").val() + " + " + parseInt($("#jobspec-clients-input").val()).toString();
	jobSpec.statsInterval = parseInt(tc.ui.newtab.statsSlider.slider("value"));
	jobSpec.requests = {};
	for (var i in tc.ui.newtab.urls) {
		jobSpec.requests[tc.ui.newtab.urls[i]] = { method: "GET", postdata: null, cookies: [] };
	}
	return jobSpec;
}

tc.ui.newtab.reviewParameters = function() {
	jobSpec = tc.ui.newtab.createJobSpec();
	var testType = $(":input[@name='jobspec-profile-input']:checked").val();
	testType = testType.charAt(0).toUpperCase() + testType.substring(1);
	var urls = "";
	for (var i in jobSpec.requests) {
		urls += i + "<br />";
	}
	var clientStr = null;
	var clientVal = null;
	switch (testType) {
		case "Stress":
			clientStr = "Requests per second";
			clientVal = $("#jobspec-clients-input").val();
			break;
		case "Benchmark":
			clientStr = "Concurrent Clients";
			clientVal = $("#jobspec-clients-input").val();
			break;
		case "Simulation":
			clientStr = "Client Function";
			clientVal = jobSpec.clientFunction;
			break;
	};
	
	$("#wizard-confirm-error").hide();
	tc.ui.newtab.review_table.fnClearTable();
	tc.ui.newtab.review_table.fnAddData([
		["Test Type", testType],
		["Duration", $("#jobspec-duration-input").val() + " " + $("#jobspec-duration-multiplier :selected").html()],
		["Max Transfer", $("#jobspec-transferLimit-input").val() + " " + $("#jobspec-transferLimit-multiplier :selected").html()],
		["Statistics Interval", jobSpec.statsInterval + " seconds"],	
		[clientStr, clientVal],
		["URLs", urls],				
	]);
	
	try {
		tc.ui.newtab.validate(jobSpec);
	}
	catch (e) {
		$("#wizard-confirm-error").show();
		$("#wizard-confirm-error").html(e);
		return;
	}
	$("#wizard-create-job-link").show();
};

tc.ui.newtab.validate = function(jobSpec) {
	if (jobSpec.profile != 0 && jobSpec.profile != 1) {
		throw "Invalid test type";
	}
	if (jobSpec.duration <= 0 || isNaN(jobSpec.duration) || typeof jobSpec.duration != "number") {
		throw "Invalid test duration";
	}
	if (jobSpec.transferLimit <= 0 || isNaN(jobSpec.transferLimit) || typeof jobSpec.transferLimit != "number") {
		throw "Invalid maximum data transfer";
	}
	if (jobSpec.clientFunction == "0 + NaN" || typeof jobSpec.clientFunction != "string") {
		throw "Invalid concurrent client settings";
	}

	// no good way to get the listing of keys in a request object
	var jsKeys = 0;
	for (var i in jobSpec.requests) {
		jsKeys += 1;
	}
	if (jsKeys == 0) {
		throw "No URLs added";
	}	
	return true;
};