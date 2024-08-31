package com.example.tr4;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class WebActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_web);

        WebView myWebView = findViewById(R.id.webview);

        // Enable JavaScript
        WebSettings webSettings = myWebView.getSettings();
        webSettings.setJavaScriptEnabled(true);

        // Handle navigation within the WebView
        myWebView.setWebViewClient(new WebViewClient());

        // Load the desired URL
        myWebView.loadUrl("https://seproject-1-oymv.onrender.com/");
    }
}