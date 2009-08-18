package cc.thundercloud.ui.client.data;


import java.util.ArrayList;
import java.util.List;
import java.util.HashMap;

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONNumber;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONNull;
import com.google.gwt.json.client.JSONString;

public class JobSpec {
	
	public enum JobProfile {
		HAMMER,
		BENCHMARK,
	};
	
	private JobProfile profile;
	private float duration;
	private float transferLimit;
	private String clientFunction;
	private int statsGranularity;
	private String userAgent;
	private List<String> urlList;
	
	public JobSpec() {
		profile = JobProfile.BENCHMARK;
		duration = (float) 60.0;//Float.POSITIVE_INFINITY;
		transferLimit = Float.POSITIVE_INFINITY;
		clientFunction = "5";
		statsGranularity = 60;		
	}
	
	public void setUrlList(List<String> urlList) {
		this.urlList = urlList;
	}
	public List<String> getUrlList() {
		return urlList;
	}

	
	public JSONObject toJson() {
		JSONObject jsonObject = new JSONObject();

		/* URL mapping */
		JSONObject requestDict = new JSONObject();
		for (int i = 0; i < urlList.size(); i++) {
			JSONObject request = new JSONObject();
			request.put("method", new JSONString("GET"));
			request.put("postdata", JSONNull.getInstance());
			request.put("cookies", new JSONArray());
			requestDict.put(urlList.get(i), request);
		}
		jsonObject.put("requests", requestDict);
		
		try {
			jsonObject.put("userAgent", new JSONString(userAgent));
		} catch (Exception e) {
			
		}
		
		jsonObject.put("transferLimit", new JSONNumber(transferLimit));
		jsonObject.put("duration", new JSONNumber(duration));
		jsonObject.put("statsGranularity", new JSONNumber(statsGranularity));
		jsonObject.put("clientFunction", new JSONString(clientFunction));				
		
		
		return jsonObject;
	}
	
}

/*
class JobProfile:
HAMMER = 0
BENCHMARK = 1

requests = {"":{}}
duration = float("inf")
transferLimit = float("inf")
clientFunction = "1"
statsGranularity = 60
userAgent = "thundercloud client/%s" % constants.VERSION
profile = JobProfile.HAMMER
*/