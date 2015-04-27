package com.chatapp.androidchat;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.text.TextUtils;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;

import com.github.nkzawa.emitter.Emitter;
import com.github.nkzawa.socketio.client.IO;
import com.github.nkzawa.socketio.client.Socket;

import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.StatusLine;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.List;

public class MessageActivity extends ActionBarActivity {

    private EditText messageInput;
    private Socket socket;
    private List<String> messages;
    private ArrayAdapter arrayAdapter;
    private ListView listView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_message);
        String friendId = getIntent().getStringExtra("friend_id");
        messages = new ArrayList<>();
        GetMessages getMessages = new GetMessages();
        getMessages.execute(friendId);
        try {
            socket = IO.socket(getString(R.string.server_address));
        } catch (URISyntaxException e) {
            e.printStackTrace();
        }
        socket.on("new message", onNewMessage);
        socket.connect();
        messageInput = (EditText) findViewById(R.id.editText);
        Button sendButton = (Button) findViewById(R.id.button);
        sendButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                attemptSend();
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        InputMethodManager imm = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
        imm.showSoftInput(messageInput, InputMethodManager.SHOW_FORCED);
    }

    private Emitter.Listener onNewMessage = new Emitter.Listener() {
        @Override
        public void call(final Object... args) {
            // TODO new message contains what all fields?
            MessageActivity.this.runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    JSONObject data = (JSONObject) args[0];
                    String message;
                    try {
                        message = data.getString("message");
                    } catch (JSONException e) {
                        return;
                    }

                    addMessage(message);
                }
            });
        }
    };

    @Override
    protected void onDestroy() {
        super.onDestroy();
        socket.off("new message");
    }

    private void addMessage(String message) {
        messages.add(message);
        arrayAdapter.notifyDataSetChanged();
        listView.setAdapter(arrayAdapter);
    }

    private void attemptSend() {
        String message = messageInput.getText().toString().trim();
        if (TextUtils.isEmpty(message)) {
            return;
        }

        messageInput.setText("");
        socket.emit("new message", message);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_message, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    private class GetMessages extends AsyncTask<String, Void, Void> {
        @Override
        protected Void doInBackground(String... params) {
            HttpClient httpClient = new DefaultHttpClient();
            try {
                SharedPreferences sharedPreferences = getSharedPreferences(getString(R.string.shared_preferences), Context.MODE_PRIVATE);
                // TODO id should be passed as GET parameter?
                HttpGet request = new HttpGet(getString(R.string.server_address) + "/get_messages?id=" + params[0]);
                request.setHeader("authorization", "basic " + sharedPreferences.getString("API_KEY", null));
                HttpResponse httpResponse = httpClient.execute(request);
                StatusLine statusLine = httpResponse.getStatusLine();
                if (statusLine.getStatusCode() == HttpStatus.SC_OK) {
                    ByteArrayOutputStream out = new ByteArrayOutputStream();
                    httpResponse.getEntity().writeTo(out);
                    JSONObject responseJSON = new JSONObject(out.toString());
                    out.close();
                    JSONArray messagesJSON = responseJSON.getJSONArray("data");
                    for (int i = 0; i < messagesJSON.length(); i++) {
                        JSONObject message = messagesJSON.getJSONObject(i);
                        messages.add(message.toString());
                    }
                } else {
                    httpResponse.getEntity().getContent().close();
                    throw new IOException(statusLine.getReasonPhrase());
                }
            } catch (IOException | JSONException e) {
                Log.d("Login", e.getMessage());
            }
            return null;
        }

        @Override
        protected void onPostExecute(Void v) {
            listView = (ListView) findViewById(R.id.listView2);
            arrayAdapter = new ArrayAdapter(getApplicationContext(), R.layout.message, messages);
            listView.setAdapter(arrayAdapter);
        }
    }
}
