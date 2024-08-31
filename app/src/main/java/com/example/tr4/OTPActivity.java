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
import android.widget.TextView;
import com.example.tr4.utils.AndroidUtil;
import com.example.tr4.utils.FirebaseUtil;
import com.example.tr4.utils.UserModel;
import com.google.firebase.FirebaseException;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.PhoneAuthCredential;
import com.google.firebase.auth.PhoneAuthOptions;
import com.google.firebase.auth.PhoneAuthProvider;
import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;
import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.TimeUnit;

public class OTPActivity extends AppCompatActivity {


    private static final long TIMEOUT_SECONDS = 60L;

    private String phoneNumber;
    private String verificationCode;
    private PhoneAuthProvider.ForceResendingToken resendingToken;

    private EditText otpInput;
    private Button nextBtn;
    private ProgressBar progressBar;
    private TextView resendOtpTextView;
    private FirebaseAuth mAuth;
    private DatabaseReference userRef;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_otpactivity);

        initViews();
        mAuth = FirebaseAuth.getInstance();
        phoneNumber = getIntent().getStringExtra("phone");
        sendOtp(phoneNumber, false);

        nextBtn.setOnClickListener(v -> verifyOtp());
        resendOtpTextView.setOnClickListener(v -> sendOtp(phoneNumber, true));
    }

    private void initViews() {
        otpInput = findViewById(R.id.login_otp);
        nextBtn = findViewById(R.id.login_next_btn);
        progressBar = findViewById(R.id.login_progress_bar);
        resendOtpTextView = findViewById(R.id.resend_otp_textview);
    }

    private void sendOtp(String phoneNumber, boolean isResend) {
        startResendTimer();
        setInProgress(true);

        PhoneAuthOptions.Builder builder = PhoneAuthOptions.newBuilder(mAuth)
                .setPhoneNumber(phoneNumber)
                .setTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
                .setActivity(this)
                .setCallbacks(new PhoneAuthProvider.OnVerificationStateChangedCallbacks() {
                    @Override
                    public void onVerificationCompleted(@NonNull PhoneAuthCredential phoneAuthCredential) {
                        AndroidUtil.showToast(getApplicationContext(), "OTP verification is done!");
                        signIn(phoneAuthCredential);
                    }

                    @Override
                    public void onVerificationFailed(@NonNull FirebaseException e) {
                        AndroidUtil.showToast(getApplicationContext(), "OTP verification failed");
                        setInProgress(false);
                    }

                    @Override
                    public void onCodeSent(@NonNull String s, @NonNull PhoneAuthProvider.ForceResendingToken forceResendingToken) {
                        super.onCodeSent(s, forceResendingToken);
                        verificationCode = s;
                        resendingToken = forceResendingToken;
                        AndroidUtil.showToast(getApplicationContext(), "OTP sent successfully");
                        setInProgress(false);
                    }
                });

        if (isResend) {
            PhoneAuthProvider.verifyPhoneNumber(builder.setForceResendingToken(resendingToken).build());
        } else {
            PhoneAuthProvider.verifyPhoneNumber(builder.build());
        }
    }

    private void verifyOtp() {
        String enteredOtp = otpInput.getText().toString();
        PhoneAuthCredential credential = PhoneAuthProvider.getCredential(verificationCode, enteredOtp);
        signIn(credential);
    }

    private void setInProgress(boolean inProgress) {
        progressBar.setVisibility(inProgress ? View.VISIBLE : View.GONE);
        nextBtn.setVisibility(inProgress ? View.GONE : View.VISIBLE);
    }

    private void signIn(PhoneAuthCredential phoneAuthCredential) {
        setInProgress(true);
        mAuth.signInWithCredential(phoneAuthCredential).addOnCompleteListener(task -> {
            setInProgress(false);
            if (task.isSuccessful()) {


                FirebaseUtil.isUserExists(phoneNumber, new FirebaseUtil.UserExistsCallback() {
                    @Override
                    public void onResult(boolean isUserExists) {
                        if (isUserExists) {
                            // User exists, navigate to MainActivity
                            saveUserDetailsInSharedPreferences(phoneNumber , FirebaseUtil.getUserName(phoneNumber));
                            navigateToMainActivity();
                        } else {
                            // User does not exist, set button click listener
                            navigateToUserNameActivity();
                        }
                    }
                });



            } else {
                AndroidUtil.showToast(getApplicationContext(), "Sign in failed: " + task.getException().getMessage());
            }
        });
    }


    private void startResendTimer() {
        resendOtpTextView.setEnabled(false);
        new Timer().scheduleAtFixedRate(new TimerTask() {
            long timeoutSeconds = TIMEOUT_SECONDS;
            @Override
            public void run() {
                runOnUiThread(() -> {
                    if (timeoutSeconds <= 0) {
                        resendOtpTextView.setText("Resend OTP");
                        resendOtpTextView.setEnabled(true);
                        cancel();
                    } else {
                        resendOtpTextView.setText("Resend OTP in " + timeoutSeconds + " seconds");
                        timeoutSeconds--;
                    }
                });
            }
        }, 0, 1000);
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
        Intent intent = new Intent(OTPActivity.this, MainActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
    }

    private void navigateToUserNameActivity() {
        Intent intent = new Intent(OTPActivity.this, UserNameActivity.class);
        intent.putExtra("phone", phoneNumber);
        startActivity(intent);
    }
}