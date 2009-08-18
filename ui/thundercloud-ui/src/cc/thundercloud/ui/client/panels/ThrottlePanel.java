package cc.thundercloud.ui.client.panels;


import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.TextBox;

public class ThrottlePanel extends HorizontalPanel {

	/* singleton stuff */
	private static class ThrottlePanelHolder {
		private static final ThrottlePanel INSTANCE = new ThrottlePanel();
	}
	public static ThrottlePanel get() {
		return ThrottlePanelHolder.INSTANCE;
	}	
	/* end singleton stuff */
	
	public ThrottlePanel() {
	
		TextBox clientsPerSec = new TextBox();
		clientsPerSec.setWidth("5em");
		clientsPerSec.setText("10");
		
		Label cpsLabel = new Label();
		cpsLabel.setText("clients/sec");
		
		this.add(clientsPerSec);
		this.add(cpsLabel);

	}
	
	
}
