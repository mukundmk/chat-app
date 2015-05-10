package com.chatapp.androidchat;

public class User {
    private String id;
    private String name;
    private String profileImageURL;
    public User(String id, String name, String profileImageURL){
        this.id = id;
        this.name = name;
        this.profileImageURL = profileImageURL;
    }

    public void setId(String id){
        this.id = id;
    }

    public void setName(String name){
        this.name = name;
    }

    public void setProfileImageURL(String profileImageURL){
        this.profileImageURL = profileImageURL;
    }

    public String getId(){
        return this.id;
    }

    public String getName(){
        return this.name;
    }

    public String getProfileImageURL(){
        return this.profileImageURL;
    }

}
