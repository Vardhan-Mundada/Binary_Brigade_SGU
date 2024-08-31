package com.example.tr4;

import androidx.appcompat.app.AppCompatActivity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;

import com.example.tr4.utils.FirebaseUtil; // Import your FirebaseUtil class

public class SplashActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "loginDetails";
    private static final String KEY_PHONE_NUMBER = "phone";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        new Handler().postDelayed(new Runnable() {
            @Override
            public void run() {
                // Check if the user is logged in via FirebaseAuth
                if (FirebaseUtil.isLoggedIn()) {
                    // User is logged in, redirect to MainActivity
                    Log.d("HACKERA" , " FROM SPLASH TO MAIN");
                    navigateToMainActivity();
                } else {
                    // User is not logged in, check SharedPreferences for login details
                    SharedPreferences sharedPreferences = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
                    String phoneNumber = sharedPreferences.getString(KEY_PHONE_NUMBER, null);

                    if (phoneNumber != null) {
                        // User is registered but not logged in, redirect to MainActivity
                        Log.d("HACKERA" , " FROM TO MAIN");
                        navigateToMainActivity();
                    } else {
                        // User is not logged in or registered, redirect to LoginActivity
                        navigateToLoginActivity();
                    }
                }
            }
        }, 2000); // Delay for 2 seconds
    }

    // Navigate to MainActivity
    private void navigateToMainActivity() {

        Intent intent = new Intent(SplashActivity.this, MainActivity.class);
        startActivity(intent);
        finish();
    }

    // Navigate to LoginActivity
    private void navigateToLoginActivity() {
        Intent intent = new Intent(SplashActivity.this, LoginActivity.class);
        startActivity(intent);
        finish();
    }
}
