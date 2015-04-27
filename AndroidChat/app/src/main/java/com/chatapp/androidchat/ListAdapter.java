package com.chatapp.androidchat;

import android.content.Context;
import android.net.Uri;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import java.util.List;

public class ListAdapter extends ArrayAdapter<User> {

    public ListAdapter(Context context, int textViewResourceId) {
        super(context, textViewResourceId);
    }

    public ListAdapter(Context context, int resource, List<User> users) {
        super(context, resource, users);
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {

        View v = convertView;

        if (v == null) {

            LayoutInflater vi;
            vi = LayoutInflater.from(getContext());
            v = vi.inflate(R.layout.list_item, null);

        }

        User user = getItem(position);

        if (user != null) {

            TextView name = (TextView) v.findViewById(R.id.textView);
            ImageView profilePicture = (ImageView) v.findViewById(R.id.imageView);

            if (name != null) {
                name.setText(user.getId());
            }

            if (profilePicture != null) {
                profilePicture.setImageURI(Uri.parse(user.getProfileImageURL()));
            }
        }

        return v;

    }

}
