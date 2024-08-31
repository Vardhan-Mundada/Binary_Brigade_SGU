package com.example.tr4;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.Toast;

import com.example.tr4.utils.FirebaseUtil;
import com.example.tr4.utils.UserModel;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

public class UserNameActivity extends AppCompatActivity {

    private EditText usernameInput;
    private Button letMeInBtn;
    private ProgressBar progressBar;
    private String phoneNumber;
    private UserModel userModel;
    private DatabaseReference userRef;

    @Override
    protected void onCreate(Bundle savedInstanceState) {

        phoneNumber = getIntent().getStringExtra("phone");

        FirebaseUtil.isUserExists(phoneNumber, new FirebaseUtil.UserExistsCallback() {
            @Override
            public void onResult(boolean isUserExists) {
                if (isUserExists) {
                    // User exists, navigate to MainActivity
                    saveUserDetailsInSharedPreferences(phoneNumber , FirebaseUtil.getUserName(phoneNumber));
                    navigateToMainActivity();
                } else {
                    // User does not exist, set button click listener
                    letMeInBtn.setOnClickListener(v -> setUsername());
                }
            }
        });


        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_user_name);

        // Initialize UI components
        initializeUI();




        userRef = FirebaseDatabase.getInstance().getReference("Users").child(phoneNumber);

        Log.d("HACKERA", String.valueOf(userRef));




    }

    private void initializeUI() {
        usernameInput = findViewById(R.id.login_username);
        letMeInBtn = findViewById(R.id.login_let_me_in_btn);
        progressBar = findViewById(R.id.login_progress_bar);
    }


    private void setUsername() {
        String username = usernameInput.getText().toString().trim();

        if (username.isEmpty() || username.length() < 3) {
            usernameInput.setError("Username length should be at least 3 chars");
            return;
        }

        setInProgress(true);

        Calendar calendar = Calendar.getInstance();

        // Subtract 3 months
        calendar.add(Calendar.MONTH, -3);

        // Format the date
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
        String lastUpdateTime = sdf.format(calendar.getTime());
        Log.d("HACKERA", lastUpdateTime + "in UserNameActivity in the setUserName");
        // Create or update the user model
        if (userModel == null) {
            userModel = new UserModel(phoneNumber, username, lastUpdateTime, new ArrayList<>());
            Log.d("HACKERA", String.valueOf(userModel));
        } else {
            userModel.setUserName(username);
        }

        // Save user model to Firebase
        userRef.setValue(userModel).addOnCompleteListener(task -> {
            setInProgress(false);
            if (task.isSuccessful()) {
                saveUserDetailsInSharedPreferences(userModel.getPhone() , userModel.getUserName());
                showToast("Username saved successfully");
                navigateToMainActivity();
            } else {
                showToast("Failed to save username");
            }
        });
    }

    private void setInProgress(boolean inProgress) {
        progressBar.setVisibility(inProgress ? View.VISIBLE : View.GONE);
        letMeInBtn.setVisibility(inProgress ? View.GONE : View.VISIBLE);
    }

    private void saveUserDetailsInSharedPreferences(String phone , String UName) {
        Log.d("HACKERA", "saveUserDetailsInSharedPreferences in UserNameActivity");
        SharedPreferences sharedPreferences = getSharedPreferences("loginDetails", MODE_PRIVATE);
        SharedPreferences.Editor editor = sharedPreferences.edit();
        editor.putString("phone", phone);
        editor.putString("username", UName);
        editor.apply();
    }

    private void navigateToMainActivity() {
        Intent intent = new Intent(UserNameActivity.this, MainActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
    }

    private void showToast(String message) {
        Toast.makeText(UserNameActivity.this, message, Toast.LENGTH_SHORT).show();
    }
}
