package cc.thundercloud.ui.client.widgets;

import cc.thundercloud.ui.client.data.JobSpec;
import cc.thundercloud.ui.client.data.UrlQueue;


import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.ButtonBase;

import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.http.client.URL;



public class StartButton extends Button {

	public StartButton() {
		super();
		this.addClickHandler(new ClickHandler() {
			public void onClick(ClickEvent clickEvent) {
				RequestBuilder request = new RequestBuilder(RequestBuilder.POST, URL.encode("http://localhost:7000/job"));
				JobSpec jobSpec = new JobSpec();
				jobSpec.setUrlList(UrlQueue.getList());
				
				request.setRequestData(jobSpec.toJson().toString());
				System.out.println(jobSpec.toJson().toString());
				request.setCallback(new RequestCallback() {

					public void onError(Request request, Throwable exception) {
						System.out.println(request.toString());
						
					}

					public void onResponseReceived(Request request,	Response response) {
						System.out.println(response);
						
					}
					
				});
				try {
					request.send();
				} catch (RequestException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
		});
		this.setText("Start");
	}

}
