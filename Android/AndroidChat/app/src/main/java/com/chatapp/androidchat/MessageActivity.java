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

import io.socket.IOAcknowledge;
import io.socket.IOCallback;
import io.socket.SocketIO;
import io.socket.SocketIOException;

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
import java.io.IOException;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

public class MessageActivity extends ActionBarActivity {

    private EditText messageInput;
    private SocketIO socket;
    private ArrayAdapter arrayAdapter;
    private ListView listView;
    private String data, friendId;
    private CryptModule crypt;
    private ArrayList<String> messages;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_message);
        messages = new ArrayList<String>();
       friendId = getIntent().getStringExtra("friend_id");
        GetMessages getMessages = new GetMessages();
        getMessages.execute(friendId);
        /**
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
        socket.off("receive message");
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
        socket.emit("receive message", message);
    */
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
            SharedPreferences sharedPreferences = getSharedPreferences(getString(R.string.shared_preferences), Context.MODE_PRIVATE);
            try {
                // TODO id should be passed as GET parameter?
                HttpGet request = new HttpGet(getString(R.string.server_address) + "/get_messages?id="+params[0]);
                request.setHeader("authorization", "Basic " + sharedPreferences.getString("API_KEY", null));
                HttpResponse httpResponse = httpClient.execute(request);
                StatusLine statusLine = httpResponse.getStatusLine();
                CryptModule crypt = new CryptModule(sharedPreferences.getString("PRIVATE_KEY",""),sharedPreferences.getString("PUBLIC_KEY",""));
                if (statusLine.getStatusCode() == HttpStatus.SC_OK) {
                    ByteArrayOutputStream out = new ByteArrayOutputStream();
                    httpResponse.getEntity().writeTo(out);
                    JSONObject responseJSON = new JSONObject(out.toString());
                    out.close();
                    JSONArray messagesJSON = responseJSON.getJSONArray("data");
                    for (int i = 0; i < messagesJSON.length(); i++) {
                        JSONArray message = messagesJSON.getJSONArray(i);
                        if(message.getString(1).equals("text"))
                            messages.add(crypt.decrypt(message.getString(2), message.getString(3)));
                    }
                } else {
                    httpResponse.getEntity().getContent().close();
                    throw new IOException(statusLine.getReasonPhrase());
                }
            } catch (Exception e) {
                Log.d("Login", e.getMessage());
            }
            HttpGet request = new HttpGet(getString(R.string.server_address) + "/get_publickey?id="+params[0]);
            request.setHeader("authorization", "Basic " + sharedPreferences.getString("API_KEY", null));
            HttpResponse httpResponse = null;
            try {
                httpResponse = httpClient.execute(request);
                StatusLine statusLine = httpResponse.getStatusLine();
                if (statusLine.getStatusCode() == HttpStatus.SC_OK) {
                    String json = EntityUtils.toString(httpResponse.getEntity());
                    Log.d("json",json);
                    data = json;
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
            return null;
        }

        @Override
        protected void onPostExecute(Void param) {
            listView = (ListView) findViewById(R.id.listView2);
            arrayAdapter = new ArrayAdapter(getApplicationContext(), R.layout.message, messages);
            arrayAdapter.setNotifyOnChange(true);
            listView.setAdapter(arrayAdapter);
            SharedPreferences sharedPreferences = getSharedPreferences(getString(R.string.shared_preferences), Context.MODE_PRIVATE);
            String apikey = sharedPreferences.getString("API_KEY","");
            Properties headers=new Properties();
            headers.setProperty("Authorization","Basic "+apikey);
            try {
                socket = new SocketIO(getString(R.string.server_address)+"/chat",headers);

            } catch (Exception e) {
                e.printStackTrace();
            }
            JSONObject responseJSON = null;
            try {
                responseJSON = new JSONObject(data);
            } catch (JSONException e) {
                e.printStackTrace();
            }
            try {
                crypt = new CryptModule(sharedPreferences.getString("PRIVATE_KEY",""),responseJSON.getString("key"),sharedPreferences.getString("PUBLIC_KEY",""));
            } catch (Exception e) {
                e.printStackTrace();
            }
            socket.addHeader("Authorization", "Basic " + apikey);
            socket.connect(new IOCallback() {
                @Override
                public void onDisconnect() {

                }

                @Override
                public void onConnect() {

                }

                @Override
                public void onMessage(String s, IOAcknowledge ioAcknowledge) {

                }

                @Override
                public void onMessage(JSONObject jsonObject, IOAcknowledge ioAcknowledge) {

                }

                @Override
                public void on(String s, IOAcknowledge ioAcknowledge, Object... objects) {
                    Log.d("event",s);
                    SharedPreferences sharedPreferences = getSharedPreferences(getString(R.string.shared_preferences), Context.MODE_PRIVATE);
                    if(s.equals("join room req")){
                        JSONObject json = new JSONObject();
                        try {
                            json.put("id",sharedPreferences.getString("ID", ""));
                            socket.emit("join room",json);
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }
                    else if(s.equals("receive message")){
                        Log.d("String", objects[0].toString());
                        try {
                            JSONObject json = new JSONObject(objects[0].toString());
                            if(json.getString("type").equals("text")) {
                                final String plaintext = crypt.decrypt(json.getString("data"), json.getString("aes_key"));
                                MessageActivity.this.runOnUiThread(new Runnable() {
                                    @Override
                                    public void run() {

                                        messages.add(plaintext);
                                        arrayAdapter.notifyDataSetChanged();
                                        listView.setAdapter(arrayAdapter);
                                    }
                                });
                                }
                            } catch (Exception e) {
                            e.printStackTrace();
                        }

                    }

                }

                @Override
                public void onError(SocketIOException e) {

                }
            });
            Button sendButton = (Button) findViewById(R.id.button);
            sendButton.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    messageInput = (EditText) findViewById(R.id.editText);
                    try {
                        SharedPreferences sharedPreferences = getSharedPreferences(getString(R.string.shared_preferences), Context.MODE_PRIVATE);
                        String[] cipher = crypt.encrypt(messageInput.getText().toString());
                        JSONObject json = new JSONObject();
                        json.put("from",sharedPreferences.getString("ID",""));
                        json.put("to",friendId);
                        json.put("type","text");
                        json.put("data",cipher[0]);
                        Log.d("a",cipher[1]);
                        json.put("key_1",cipher[1]);
                        json.put("key_2",cipher[2]);
                        socket.emit("send message",json);
                        messages.add(messageInput.getText().toString());
                        arrayAdapter.notifyDataSetChanged();
                        listView.setAdapter(arrayAdapter);
                        messageInput.setText("");
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            });
        }
    }
}
