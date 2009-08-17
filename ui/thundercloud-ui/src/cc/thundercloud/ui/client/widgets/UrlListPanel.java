package cc.thundercloud.ui.client.widgets;


import java.util.ArrayList;

import cc.thundercloud.ui.client.data.UrlQueue;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;

public class UrlListPanel extends VerticalPanel {
	
	/* singleton stuff */
	private static class UrlQueuePanelHolder {
		private static final UrlListPanel INSTANCE = new UrlListPanel();
	}
	public static UrlListPanel get() {
		return UrlQueuePanelHolder.INSTANCE;
	}	
	/* end singleton stuff */
	
	
	final FlexTable urlTable;
	private ArrayList<String> urlList = new ArrayList<String>();
	private int index = 0;
	
	private UrlListPanel() {
		urlTable = new FlexTable();
		urlTable.setWidth("100%");
		this.add(urlTable);
		this.setWidth("100%");
	}
	
	public void addUrl(final String url) {
		Label urlLabel = new Label();
		urlLabel.setText(url);		
		
		Button removeButton = new Button();
		removeButton.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent clickEvent) {
				for (int i = 0; i < urlTable.getRowCount(); i++) {
					if (url.equals(((Grid) urlTable.getWidget(i, 0)).getText(0, 0))) {
						urlTable.removeRow(i);
						break;
					}
				}
				urlList.remove(url);
			}
		});
		removeButton.setText("X");
				
		Grid g = new Grid(1, 2);
		g.setWidget(0, 0, urlLabel);
		g.setWidget(0, 1, removeButton);
//		g.setWidth("100%");
		urlTable.setWidget(urlTable.getRowCount(), 0, g);
		urlList.add(url);
	}
	
	public boolean hasUrl(final String url) {
		return urlList.contains(url);
	}
	
	public boolean validateUrl(final String url) {
		return true;
	}
	
}
