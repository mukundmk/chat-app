package com.chatapp.androidchat;

import android.content.Context;
import android.net.Uri;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import java.util.List;

public class ListAdapter extends ArrayAdapter<User> {

    private final Context context;

    public ListAdapter(Context context, int resource, List<User> users) {
        super(context, resource, users);
        this.context = context;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {

        LayoutInflater inflater = (LayoutInflater) context.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        View v = inflater.inflate(R.layout.list_item, parent, false);

        User user = getItem(position);

        if (user != null) {

            TextView name = (TextView) v.findViewById(R.id.textView);
            ImageView profilePicture = (ImageView) v.findViewById(R.id.imageView);

            if (name != null) {

                name.setText(user.getName());
            }

            if (profilePicture != null && user.getProfileImageURL()!=null) {
                profilePicture.setImageURI(Uri.parse(user.getProfileImageURL()));
            }
        }

        return v;

    }

}
