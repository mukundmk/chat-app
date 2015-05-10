package com.chatapp.androidchat;

import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.AsyncTask;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import java.io.InputStream;
import java.net.URL;
import java.net.URLConnection;
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
                new DownloadImageTask(profilePicture).execute(user.getProfileImageURL());
            }
        }

        return v;

    }
}
class DownloadImageTask extends AsyncTask<String, Void, Bitmap> {
    ImageView bmImage;

    public DownloadImageTask(ImageView bmImage) {
        this.bmImage = bmImage;
    }

    protected Bitmap doInBackground(String... urls) {
        String urldisplay = urls[0];
        Bitmap mIcon11 = null;
        try {
            URL url = new URL(urldisplay);
            URLConnection uc = url.openConnection();
            uc.setRequestProperty("Authorization","Basic " + HomeScreen.getApiKey());
            InputStream in = uc.getInputStream();
            mIcon11 = BitmapFactory.decodeStream(in);
        } catch (Exception e) {
            Log.e("Error", e.getMessage());
            e.printStackTrace();
        }
        return mIcon11;
    }

    protected void onPostExecute(Bitmap result) {
        bmImage.setImageBitmap(result);
    }
}
