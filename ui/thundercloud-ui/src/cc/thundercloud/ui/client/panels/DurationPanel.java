package cc.thundercloud.ui.client.panels;


import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TextBox;

public class DurationPanel extends HorizontalPanel {

	/* singleton stuff */
	private static class DurationPanelHolder {
		private static final DurationPanel INSTANCE = new DurationPanel();
	}
	public static DurationPanel get() {
		return DurationPanelHolder.INSTANCE;
	}	
	/* end singleton stuff */
	
	public DurationPanel() {
	
		ListBox durationUnits = new ListBox();
		durationUnits.addItem("seconds");
		durationUnits.addItem("minutes");
		durationUnits.addItem("hours");
		durationUnits.setSelectedIndex(1);
		
		TextBox duration = new TextBox();
		duration.setWidth("2em");
		
		this.add(duration);
		this.add(durationUnits);		

	}
	
	
}
