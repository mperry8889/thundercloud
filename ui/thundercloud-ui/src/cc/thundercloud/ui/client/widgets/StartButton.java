package cc.thundercloud.ui.client.widgets;

import cc.thundercloud.ui.client.data.JobSpec;
import cc.thundercloud.ui.client.data.UrlQueue;

import com.google.gwt.dom.client.Element;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ButtonBase;

public class StartButton extends Button {

	public StartButton() {
		super();
		this.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent clickEvent) {
				JobSpec jobSpec = new JobSpec();
				//jobSpec.setUrlList(UrlQueue.getList());
			}
		});
		this.setText("Start");
	}

}
