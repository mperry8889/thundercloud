package cc.thundercloud.ui.client.widgets;

import com.google.gwt.dom.client.Element;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ButtonBase;

public class PauseButton extends Button {

	enum togglePosition {
		PAUSED, 
		RESUMED
	};
	
	togglePosition buttonPosition = togglePosition.RESUMED;
	
	public PauseButton() {
		super();
		this.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent clickEvent) {
				toggle();
			}
		});
		this.setText("Pause");
	}
	
	public void toggle() {
		if (buttonPosition == togglePosition.PAUSED) {
			buttonPosition = togglePosition.RESUMED;
			this.setText("Pause");
		}
		else {
			buttonPosition = togglePosition.PAUSED;
			this.setText("Resume");
		}
	}

}
