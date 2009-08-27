if (tc == null) { 
	var tc = new Object();
}
if (tc.ui == null) { 
	tc.ui = new Object();
}

tc.ui.wizard = new Object();
tc.ui.jobId = null;

$(document).ready(function() {
	/* OBJECT SETUP */
	tc.ui.wizard.tabs = $("#main-tabs").tabs({
		//disabled: [2],
	});	
	
	/* HELP BUTTONS */
	$(".help-link-show").click(function() {
		var elem = "#" + $(this).attr("id") + "-element";
		$(elem).show("normal");
	});
	
	$(".help-link-hide").click(function() {
		$(this).parent().hide("normal");
	}); 
 });