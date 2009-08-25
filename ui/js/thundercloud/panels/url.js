tc.panel.url = new Object();

tc.panel.url.err = function(errorMsg) {
	if ($("#add-url-errorMsg").is(":hidden")) {
		$("#add-url-errorMsg").html(errorMsg);
		$("#add-url-errorMsg").fadeIn("normal");
	}
	
};
tc.panel.url.clearErr = function() {
	$("#add-url-errorMsg").fadeOut("normal");
};
tc.panel.url.clearAll = function() {
	tc.panel.url.clearErr();
	$("#add-url-input").val("");
	$("#add-url-getCssJsImg").attr("checked", false);	
};

tc.panel.url.del = function(value) {
	tc.data.urlList.del(value);
};

/* Note: this function has to be run only after the first URL
 * has been added.  Otherwise the "#urlList tbody td" address
 * won't resolve, because it doesn't exist in the page.
 */
tc.panel.url.activateRowClicks = function() {
	$(".urlList-remove").click(function(event) {
		_rowIndex = oUrlList.fnGetPosition($(this).parent()[0])[0];
		_url = oUrlList.fnGetData(_rowIndex)[0];
		oUrlList.fnDeleteRow(_rowIndex);
		tc.panel.url.del(_url);
	});
};

var oUrlList;

$(document).ready(function() {
	
	//XXX REMOVE
	$("#add-url-input").val("http://unshift.net");
	

	oUrlList = $("#urlList").dataTable({
		"bPaginate": false,	
		"bInfo": false,
		"bSort": false,
		"bFilter": false,
		"oLanguage": {
			"sZeroRecords": "No URLs added",
		},
	});

	$("#add-url-errorMsg").hide();


	$("#add-url-button").click(function() {
		_val = $("#add-url-input").val();
		if (_val == "") {
			tc.panel.url.err("No URL specified");
			return;
		}
		try {
			tc.data.urlList.add(_val);
		}
		catch (e) {
			tc.panel.url.err(e);
			return;
		}
		oUrlList.fnAddData([_val, '<a href="javascript:;" class="urlList-remove">Remove</a>']);
		tc.panel.url.clearAll();
		tc.panel.url.activateRowClicks();
	});
	
	$("#add-url-clear-button").click(function() {
		tc.panel.url.clearAll();
	});


});
