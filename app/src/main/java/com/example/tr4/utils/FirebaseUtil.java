package com.example.tr4.utils;

import android.content.SharedPreferences;
import android.util.Log;

import androidx.annotation.NonNull;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.android.gms.tasks.TaskCompletionSource;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;



public class FirebaseUtil {

    // Get the current user's ID


    private static DatabaseReference mDatabase;
// ...

    public static String currentUserId() {
        return FirebaseAuth.getInstance().getCurrentUser() != null ? FirebaseAuth.getInstance().getUid() : null;
    }


    // Check if the user is logged in
    public static boolean isLoggedIn() {
        return currentUserId() != null;
    }

    // Get a reference to the current user's details in the Realtime Database
    public static DatabaseReference currentUserDetails() {


        String userId = currentUserId();
        if (userId != null) {
            // Assuming userId is the mobile number used as a key in the Realtime Database
            return FirebaseDatabase.getInstance().getReference("Users").child(userId);
        } else {
            return null; // Return null if there is no logged-in user
        }
    }

    // Convert a Unix timestamp to a string formatted as HH:MM
    public static String timestampToString(long timestamp) {
        return new SimpleDateFormat("HH:mm", Locale.getDefault()).format(new Date(timestamp));
    }

    // Log out the current user
    public static void logout() {
        FirebaseAuth.getInstance().signOut();
    }

    // Example of an asynchronous operation to fetch user details
    public static Task<DataSnapshot> getUserDetails() {
        final TaskCompletionSource<DataSnapshot> taskCompletionSource = new TaskCompletionSource<>();
        DatabaseReference userRef = currentUserDetails();
        if (userRef != null) {
            userRef.addListenerForSingleValueEvent(new ValueEventListener() {
                @Override
                public void onDataChange(@NonNull DataSnapshot dataSnapshot) {
                    taskCompletionSource.setResult(dataSnapshot);
                }

                @Override
                public void onCancelled(@NonNull DatabaseError databaseError) {
                    taskCompletionSource.setException(databaseError.toException());
                }
            });
        } else {
            taskCompletionSource.setException(new Exception("No user logged in"));
        }
        return taskCompletionSource.getTask();
    }

    // Get the user's name from the Realtime Database
    public static String getUserName(String mobNo) {

        mDatabase = FirebaseDatabase.getInstance().getReference();


        final String[] re = {""};
        mDatabase.child("Users").child(mobNo).child("userName").get().addOnCompleteListener(new OnCompleteListener<DataSnapshot>() {
            @Override
            public void onComplete(@NonNull Task<DataSnapshot> task) {
                if (!task.isSuccessful()) {
                    Log.d("HACKERA", "Error getting data", task.getException());
                }
                else {
                    Log.d("HACKERA", String.valueOf(task.getResult().getValue()));
                    re[0] = String.valueOf(task.getResult().getValue()) ;

                }

            }
        });


       return re[0];

    }


    public interface UserExistsCallback {
        void onResult(boolean exists);
    }

    public static void isUserExists(String mobNo, UserExistsCallback callback) {
        mDatabase = FirebaseDatabase.getInstance().getReference();

        mDatabase.child("Users").child(mobNo).child("userName").get().addOnCompleteListener(new OnCompleteListener<DataSnapshot>() {
            @Override
            public void onComplete(@NonNull Task<DataSnapshot> task) {
                if (!task.isSuccessful()) {
                    Log.d("HACKERA", "USER NOT FOUND IN FireBaseUtil", task.getException());
                    callback.onResult(false);
                } else {
                    Log.d("HACKERA", String.valueOf(task.getResult().getValue()) + " IN FireBaseUtil");
                    callback.onResult(task.getResult().exists());
                }
            }
        });
    }




}
