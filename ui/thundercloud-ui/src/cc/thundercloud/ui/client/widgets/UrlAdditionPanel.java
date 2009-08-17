package cc.thundercloud.ui.client.widgets;

import com.google.gwt.dom.client.Text;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Hyperlink;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.ToggleButton;
import com.google.gwt.user.client.ui.VerticalPanel;

import cc.thundercloud.ui.client.widgets.UrlListPanel;

public class UrlAdditionPanel extends VerticalPanel {

	/* singleton stuff */
	private static class UrlAdditionPanelHolder {
		private static final UrlAdditionPanel INSTANCE = new UrlAdditionPanel();
	}
	public static UrlAdditionPanel get() {
		return UrlAdditionPanelHolder.INSTANCE;
	}	
	/* end singleton stuff */
		
	
	final ListBox httpMethods;
	final TextBox urlBox;
	final Button addButton;
	final Label errorMsg;
	final Hyperlink clearErrorMsg;
	
	private UrlListPanel urlListPanel = UrlListPanel.get();
	
	public UrlAdditionPanel() {
		httpMethods = new ListBox();
		urlBox = new TextBox();
		addButton = new Button();
		errorMsg = new Label();

		/* build the panel */
		HorizontalPanel urlBar = new HorizontalPanel();
		HorizontalPanel errorPanel = new HorizontalPanel();
		
		urlBox.setText("URL...");
		urlBox.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent clickEvent) {
				urlBox.setText("");
			}
		});
		urlBox.setWidth("100%");
		
		final CheckBox cssJsImgToggle = new CheckBox();
		cssJsImgToggle.setText("Get CSS/JS/Images");
		
		errorMsg.setHeight("2em");
		clearErrorMsg = new Hyperlink();
		clearErrorMsg.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent clickEvent) {
				clearError();
			}
		});
		clearErrorMsg.setText("(clear)");
		clearErrorMsg.setVisible(false);
		
		
		addButton.setText("Add");
		addButton.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent clickEvent) {
				String url = urlBox.getText();
				if (urlListPanel.hasUrl(url)) {
					postError("ERROR!  URL must be unique");
					return;
				}
				if (!urlListPanel.validateUrl(url)) {
					postError("Invalid URL, please try again");
					return;
				}
				urlListPanel.addUrl(url);
				clearError();
				urlBox.setText("URL...");
			}
		});
		
		urlBar.add(urlBox);
		urlBar.add(addButton);
		urlBar.setWidth("100%");
		
		errorPanel.add(errorMsg);
		errorPanel.add(clearErrorMsg);
		
		this.add(urlBar);
		this.add(cssJsImgToggle);
		this.add(errorPanel);
		this.setWidth("100%");
	}
	
	public void postError(String msg) {
		errorMsg.setText(msg);
		clearErrorMsg.setVisible(true);
	}
	public void clearError() {
		errorMsg.setText("");
		clearErrorMsg.setVisible(false);
	}
	
}
