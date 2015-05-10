package com.chatapp.androidchat;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.drawable.BitmapDrawable;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.RelativeLayout;

import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.StatusLine;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.List;


public class HomeScreen extends Activity {

    private static String apiKey;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home_screen);
        getWindow().setNavigationBarColor(Color.parseColor("#01579b"));
        SharedPreferences sharedPreferences = getSharedPreferences(getString(R.string.shared_preferences), Context.MODE_PRIVATE);
        apiKey = sharedPreferences.getString("API_KEY", null);
        GetFriendsList getFriendsList = new GetFriendsList();
        getFriendsList.execute();
    }
    public static String getApiKey(){
        return apiKey;
    }

    public class GetFriendsList extends AsyncTask<Void, Void, List<User>>{

        @Override
        protected List<User> doInBackground(Void... params) {
            HttpClient httpClient = new DefaultHttpClient();
            List<User> friendsDetails = new ArrayList<User>();
            try {
                SharedPreferences sharedPreferences = getSharedPreferences(getString(R.string.shared_preferences), Context.MODE_PRIVATE);
                HttpGet request = new HttpGet(getString(R.string.server_address) + "/get_friends");
                request.setHeader("Authorization", "Basic " + sharedPreferences.getString("API_KEY", null));
                HttpResponse httpResponse = httpClient.execute(request);
                StatusLine statusLine = httpResponse.getStatusLine();
                if (statusLine.getStatusCode() == HttpStatus.SC_OK) {
                    String json =  EntityUtils.toString(httpResponse.getEntity());
                    JSONObject responseJSON = new JSONObject(json);
                    JSONArray friends = responseJSON.getJSONArray("friends");
                    for(int i=0; i<friends.length(); i++){
                        JSONObject userDetails = friends.getJSONObject(i);
                        User user = new User(userDetails.getString("id"), userDetails.getString("name"),getString(R.string.server_address) +"/get_image?id="+userDetails.getString("id"));
                        friendsDetails.add(user);
                    }
                    return friendsDetails;
                }
                else{
                    httpResponse.getEntity().getContent().close();
                    throw new IOException(statusLine.getReasonPhrase());
                }
            } catch (IOException e) {
                Log.d("Login", e.getMessage());
            } catch (JSONException e) {
                Log.d("Login", e.getMessage());
            }
            return null;
        }

        @Override
        protected void onPostExecute(final List<User> friendsList){
            ListView listView = (ListView) findViewById(R.id.listView);
            ListAdapter listAdapter = new ListAdapter(getApplicationContext(), R.layout.list_item, friendsList);
            listView.setAdapter(listAdapter);
            listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
                @Override
                public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                    ImageView iw = (ImageView) ((RelativeLayout) view).getChildAt(0);
                    Bitmap bmp = ((BitmapDrawable) iw.getDrawable()).getBitmap();
                    try {
                        String filename = "bitmap.png";
                        FileOutputStream stream = openFileOutput(filename, Context.MODE_PRIVATE);
                        bmp.compress(Bitmap.CompressFormat.PNG, 100, stream);
                        stream.close();
                        bmp.recycle();
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                    Intent messageActivityIntent = new Intent(getApplicationContext(), MessageActivity.class);
                    messageActivityIntent.putExtra("friend_id", friendsList.get(position).getId());
                    messageActivityIntent.putExtra("friend_name", friendsList.get(position).getName());
                    startActivity(messageActivityIntent);
                }
            });
        }
    }
}
