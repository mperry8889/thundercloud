package cc.thundercloud.ui.client.panels;


import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TextBox;

public class TransferPanel extends HorizontalPanel {

	/* singleton stuff */
	private static class BandwidthPanelHolder {
		private static final TransferPanel INSTANCE = new TransferPanel();
	}
	public static TransferPanel get() {
		return BandwidthPanelHolder.INSTANCE;
	}	
	/* end singleton stuff */
	
	public TransferPanel() {
	
		ListBox transferUnits = new ListBox();
		transferUnits.addItem("KB");
		transferUnits.addItem("MB");
		transferUnits.addItem("GB");
		transferUnits.addItem("TB");
		transferUnits.setSelectedIndex(2);
		
		TextBox transfer = new TextBox();
		transfer.setWidth("3em");
		
		this.add(transfer);
		this.add(transferUnits);	

	}
	
	
}
