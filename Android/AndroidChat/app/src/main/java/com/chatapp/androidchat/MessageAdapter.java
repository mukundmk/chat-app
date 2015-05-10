package com.chatapp.androidchat;


import android.content.Context;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import java.util.List;

public class MessageAdapter extends ArrayAdapter<Message> {

    public static final int DIRECTION_INCOMING = 1;
    public static final int DIRECTION_OUTGOING = 0;
    private final Context context;

    public MessageAdapter(Context context, int resource, List<Message> messages) {
        super(context, resource, messages);
        this.context = context;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup viewGroup) {
        LayoutInflater inflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        Message message = getItem(position);
        {
            int res = 0;
            Log.d("direction", message.direction + "");
            if (message.direction == DIRECTION_INCOMING) {
                res = R.layout.message_left;
            } else if (message.direction == DIRECTION_OUTGOING) {
                res = R.layout.message_right;
            }
            convertView = inflater.inflate(res, viewGroup, false);
        }

        TextView txtMessage = (TextView) convertView.findViewById(R.id.txtMessage);
        txtMessage.setText(message.message);

        return convertView;
    }
}