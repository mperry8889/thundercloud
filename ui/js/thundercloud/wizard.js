$(document).ready(function() {
	/* OBJECT SETUP */
	var $main_tabs = $("#main-tabs").tabs({
		disabled: [2],
	});
	var statsSlider = $("#jobspec-statsGranularity").slider({
			value: 5,
			min: 1,
			max: 60,
			step: 1,
			slide: function(event, ui) {
				$("#amount").val('$' + ui.value);
			}
	});             

	var url_table = $("#jobspec-url-list").dataTable({
		"bPaginate": false,	
		"bInfo": false,
		"bSort": false,
		"bFilter": false,
		"oLanguage": {
			"sZeroRecords": "No URLs added",
		},
	});
	url_table.fnAddData(["http://www.unshift.net", '<a href="javascript:;" class="jobspec-url-list-remove">Remove</a>']);
    
    $("#dashboard-progress").progressbar({ value: 27 });  
	
	
	
    
    /* JOB SETUP */
 	var $wizard_tabs = $("#wizard-workflow").tabs({
 		disabled: [1,2,3],
 	});
 	
	$(":input[@name='jobspec-profile-input']").click(function() {
		switch (parseInt($(":input[@name='jobspec-profile-input']:checked").val())) {
			case 0:
				$("#wizard-concurrency").html("Requests/sec");
				$("#wizard-concurrency-help").html("how many requests/sec");
				break;
			case 1:
				$("#wizard-concurrency").html("Concurrent clients");
				$("#wizard-concurrency-help").html("how many clients");
				break;
			default:
		}				
		$wizard_tabs.tabs("enable", 1);
		$wizard_tabs.tabs("enable", 2);
		$wizard_tabs.tabs("enable", 3);
	});

	var checkComplete = function() {
		return true;
	};


	
	
	/* JOB CREATION */
	$("#create-job-link").click(function() {
		jobSpec = new tc.api.JobSpec();
		jobSpec.profile = parseInt($(":input[@name='jobspec-profile-input']:checked").val());
		jobSpec.duration = parseInt($("#jobspec-duration-input").val() * $(".jobspec-duration-multiplier").val());
		jobSpec.maxTransfer = parseInt($("#jobspec-maxTransfer-input").val() * $(".jobspec-maxTransfer-multiplier").val());
		jobSpec.clientFunction = $("#jobspec-clientFunction-input").val().toString();
		jobSpec.statsGranularity = parseInt(statsSlider.slider("value"));
		jobSpec.requests = { "http://unshift.net": { method: "GET", postdata: null, cookies: [] }};
		tc.api.createJob(jobSpec, function(jobId) {
			$main_tabs.tabs("enable", 2);
			$main_tabs.tabs("select", 2);		
			tc.api.startJob(jobId);	
		});
		return true;
	});

	
	
	
	/* HELP BUTTONS */
	$(".help-link-show").click(function() {
		var elem = "#" + $(this).attr("id") + "-element";
		$(elem).show("normal");
	});
	
	$(".help-link-hide").click(function() {
		$(this).parent().hide("normal");
	});   
	/* END HELP BUTONS */     
 });