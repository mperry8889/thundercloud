var tc = new Object();
tc.data = new Object();
tc.panel = new Object();


/* URL list */
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

