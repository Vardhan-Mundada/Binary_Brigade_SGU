package com.example.tr4.utils;

import com.google.firebase.database.IgnoreExtraProperties;

import java.util.List;
import java.util.Date;

@IgnoreExtraProperties
public class UserModel {
    private String phone;
    private String username;
    private String dateUpdated;
    private List<String> messages;

    public UserModel() {
        // Default constructor required for calls to DataSnapshot.getValue(UserModel.class)
    }

    public UserModel(String phone, String username, String dateUpdated, List<String> messages) {
        this.phone = phone;
        this.username = username;
        this.dateUpdated = dateUpdated;
        this.messages = messages;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getUserName() {
        return username;
    }

    public void setUserName(String username) {
        this.username = username;
    }

    public String getDateUpdated() {
        return dateUpdated;
    }

    public void setDateUpdated(String dateUpdated) {
        this.dateUpdated = dateUpdated;
    }

    public List<String> getMessages() {
        return messages;
    }

    public void setMessages(List<String> messages) {
        this.messages = messages;
    }

    public void addMessage(String message) {
        this.messages.add(message);
    }

}