$(document).ready(function() {
	var $main_tabs = $("#main-tabs").tabs({
		disabled: [2],
	});
	
	$("#jobspec-statsGranularity").slider({
			value: 5,
			min: 1,
			max: 60,
			step: 1,
			slide: function(event, ui) {
				$("#amount").val('$' + ui.value);
			}
	});
	$("#dashboard-progress").progressbar({ value: 27 });               

    
    
    /* JOB SETUP WORKFLOW TABS */
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


	
	$("#dashboard-link").click(function() {
		$main_tabs.tabs("enable", 2);
		$main_tabs.tabs("select", 2);
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