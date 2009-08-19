var thundercloud = new Object();
thundercloud.util = new Object();

thundercloud.util.clearInnerHtml = function (id) {
		document.getElementById(id).innerHTML = "";
};
thundercloud.util.clearValue = function (id) {
		document.getElementById(id).value = "";
};


/* URL ADDITION PANEL */

function clearUrlPanel() {
	$("#add-url-input").val("");
	$("#add-url-errorMsg").html("");
	$("#add-url-getCssJsImg").attr("checked", false);	
}

var oAddUrlButton = new YAHOO.widget.Button("add-url-button");
$("#add-url-input").val("http://unshift.net");
oAddUrlButton.on("click", function (p_oEvent) {
	_value = $("#add-url-input").val();
	if (_value == "") {
		$("#add-url-errorMsg").html("No URL given");
		return;
	}
	//if (!thundercloud.util.validateUrl(_value)) {
	//	$("#add-url-errorMsg").html("Invalid URL");
	//	return;
	//}
	if ($("#add-url-getCssJsImg").attr("checked")) {
	//	
	}           
	
	oUrlList.addRow({Index: 0, Method: "GET", URL: _value, Actions: "Edit | Remove"});
	clearUrlPanel();
});

var oClearUrlButton = new YAHOO.widget.Button("add-url-clear-input-button");
oClearUrlButton.on("click", function (p_oEvent) {
	clearUrlPanel();
});


/* URL LIST */

var oUrlListColumns = [
	{key: "Index", resizeable: false},
    {key: "Method", resizeable: false},
	{key: "URL", resizeable: false},
	{key: "Actions", resizeable: false},
];
var oUrlListDataSource = YAHOO.util.DataSource([]);
oUrlListDataSource.responseType = YAHOO.util.DataSource.TYPE_JSARRAY;
oUrlListDataSource.responseSchema = {
	fields: ["Index", "Method", "URL", "Actions"]
};
var oUrlList = new YAHOO.widget.DataTable("urlList", oUrlListColumns, oUrlListDataSource);
oUrlList.hideColumn("Index");


/* ACTION BUTTONS */

