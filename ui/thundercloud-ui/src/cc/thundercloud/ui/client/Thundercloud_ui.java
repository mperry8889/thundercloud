package cc.thundercloud.ui.client;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyUpEvent;
import com.google.gwt.event.dom.client.KeyUpHandler;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.CheckBox;
import com.google.gwt.user.client.ui.DialogBox;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RootPanel;
import com.google.gwt.user.client.ui.TabPanel;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.VerticalPanel;

import cc.thundercloud.ui.client.panels.ButtonPanel;
import cc.thundercloud.ui.client.panels.DurationPanel;
import cc.thundercloud.ui.client.panels.ThrottlePanel;
import cc.thundercloud.ui.client.panels.TransferPanel;
import cc.thundercloud.ui.client.panels.UrlAdditionPanel;
import cc.thundercloud.ui.client.panels.UrlListPanel;
import cc.thundercloud.ui.client.widgets.PauseButton;
import cc.thundercloud.ui.client.widgets.StartButton;
import cc.thundercloud.ui.client.widgets.StopButton;

public class Thundercloud_ui implements EntryPoint {
	public void onModuleLoad() {
		RootPanel.get().setWidth("100%");
		RootPanel.get().add(UrlAdditionPanel.get());
		RootPanel.get().add(ThrottlePanel.get());
		RootPanel.get().add(TransferPanel.get());
		RootPanel.get().add(DurationPanel.get());
		RootPanel.get().add(ButtonPanel.get());
		RootPanel.get().add(UrlListPanel.get());
	}
}
