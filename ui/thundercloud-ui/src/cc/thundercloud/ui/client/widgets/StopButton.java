package cc.thundercloud.ui.client.widgets;

import com.google.gwt.dom.client.Element;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ButtonBase;

public class StopButton extends Button {

	public StopButton() {
		super();
		this.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent clickEvent) {
				
			}
		});
		this.setText("Stop");
	}

}
