package com.example.tiktokcleaner;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.WebDriver;

public class ChromeDriverManager {

public static WebDriver createWithUserProfile(String userDataDir, String profileDir) {
ChromeOptions options = new ChromeOptions();
if (userDataDir != null && !userDataDir.isEmpty()) {
options.addArguments("user-data-dir=" + userDataDir);
}
if (profileDir != null && !profileDir.isEmpty()) {
options.addArguments("--profile-directory=" + profileDir);
}
return new ChromeDriver(options);
}

public static WebDriver attachToDebuggingChrome(String debuggerAddress) {
ChromeOptions options = new ChromeOptions();
options.setExperimentalOption("debuggerAddress", debuggerAddress);
return new ChromeDriver(options);
}

public static WebDriver createStandardDriver() {
ChromeOptions options = new ChromeOptions();
return new ChromeDriver(options);
}
}