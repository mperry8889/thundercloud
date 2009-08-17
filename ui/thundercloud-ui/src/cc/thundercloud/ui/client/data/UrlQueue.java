package cc.thundercloud.ui.client.data;

import java.util.ArrayList;
import java.util.List;
import java.util.Queue;


public class UrlQueue {

	/* singleton stuff */
	private static class UrlQueuePanelHolder {
		private static final UrlQueue INSTANCE = new UrlQueue();
	}
	public static UrlQueue get() {
		return UrlQueuePanelHolder.INSTANCE;
	}	
	/* end singleton stuff */
	
	private static ArrayList<String> urlList = new ArrayList<String>();
	
	public void add(String url) throws Exception {
		if (urlList.contains(url)) {
			throw new Exception();
		}
		urlList.add(url);
	}
	
	public void remove(String url) {
		urlList.remove(url);
	}
	
	public static List<String> getList() {
		return urlList;
	}
	
}
