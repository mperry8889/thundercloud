if (tc == null) { 
	var tc = new Object();
}
if (tc.ui == null) {
	tc.ui = new Object();
}
tc.ui.newtab = new Object();
tc.ui.newtab.urls = [];
tc.ui.newtab.profile = 0;

$(document).ready(function() {
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
 		//disabled: [1,2,3],
 		select: function(event, ui) {
 			// review & confirm tab. have to use numerical index
 			if (ui.index == 3) {
 				tc.ui.newtab.reviewParameters();
 			}
 		},
 	});
 	
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
	
	var checkComplete = function() {
		return true;
	};

	
	
	/* JOB CREATION */
	$("#create-job-link").click(function() {
		jobSpec = tc.ui.newtab.createJobSpec();
		tc.api.createJob(jobSpec, function(jobId) {
			tc.ui.wizard.tabs.tabs("enable", 2);
			tc.ui.wizard.tabs.tabs("select", 2);
			tc.api.startJob(jobId);	
		});
		return true;
	});	
	
	
	
	
	
});

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
	jobSpec.maxTransfer = parseInt($("#jobspec-maxTransfer-input").val() * $("#jobspec-maxTransfer-multiplier").val());
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
	$("#wizard-confirm-parameters").html(jobSpec.profile+"<br>"+jobSpec.clientFunction);
	
};