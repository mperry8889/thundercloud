package cc.thundercloud.ui.client.panels;


import cc.thundercloud.ui.client.widgets.StartButton;
import cc.thundercloud.ui.client.widgets.PauseButton;
import cc.thundercloud.ui.client.widgets.StopButton;

import com.google.gwt.user.client.ui.HorizontalPanel;

public class ButtonPanel extends HorizontalPanel {
	/* singleton stuff */
	private static class ButtonPanelHolder {
		private static final ButtonPanel INSTANCE = new ButtonPanel();
	}
	public static ButtonPanel get() {
		return ButtonPanelHolder.INSTANCE;
	}	
	/* end singleton stuff */
	
	public ButtonPanel() {
		this.add(new StartButton());
		this.add(new PauseButton());
		this.add(new StopButton());
	}
	
}
