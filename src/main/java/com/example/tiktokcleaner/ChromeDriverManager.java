package com.example.tiktokcleaner;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

import java.io.BufferedReader;
import java.io.InputStreamReader;

public class ChromeDriverManager {

    private static final String DRIVER_PATH = "/usr/local/bin/chromedriver";
    private static final String CHROME_PROFILE_PATH = "/Users/marnirabinowitz/Library/Application Support/Google/Chrome"; // adjust for your OS
    private static final String PROFILE_DIRECTORY = "Default"; // or another profile folder name

    public static WebDriver setupChromeDriver() throws Exception {
        // Validate ChromeDriver exists
        if (!isDriverValid(DRIVER_PATH)) {
            throw new RuntimeException("ChromeDriver not found or not executable at: " + DRIVER_PATH);
        }

        // Validate Chrome version matches driver version (optional)
        String chromeVersion = getChromeVersion();
        String driverVersion = getChromeDriverVersion(DRIVER_PATH);
        if (!chromeVersion.split("\\.")[0].equals(driverVersion.split("\\.")[0])) {
            throw new RuntimeException("ChromeDriver version (" + driverVersion + ") does not match Chrome version (" + chromeVersion + ")");
        }

        System.setProperty("webdriver.chrome.driver", DRIVER_PATH);

        // Set up ChromeOptions to reuse your existing profile
        ChromeOptions options = new ChromeOptions();
        options.addArguments("user-data-dir=" + CHROME_PROFILE_PATH);
        options.addArguments("--profile-directory=" + PROFILE_DIRECTORY);
        // Avoid headless mode; let Selenium show the browser
        // options.addArguments("--headless"); // <-- do NOT use headless

        System.out.println("Using local ChromeDriver at: " + DRIVER_PATH);
        System.out.println("Chrome version: " + chromeVersion + ", ChromeDriver version: " + driverVersion);
        System.out.println("Using Chrome profile: " + CHROME_PROFILE_PATH + " / " + PROFILE_DIRECTORY);

        // Launch ChromeDriver with the profile
        return new ChromeDriver(options);
    }

    private static boolean isDriverValid(String path) {
        try {
            Process process = new ProcessBuilder(path, "--version").start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String versionLine = reader.readLine();
            int exitCode = process.waitFor();
            return exitCode == 0 && versionLine != null && !versionLine.isEmpty();
        } catch (Exception e) {
            return false;
        }
    }

    private static String getChromeVersion() throws Exception {
        Process process = new ProcessBuilder(
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "--version"
        ).start();
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        String versionLine = reader.readLine();
        if (versionLine == null || versionLine.isEmpty()) throw new RuntimeException("Cannot detect Chrome version");
        return versionLine.replace("Google Chrome ", "").trim();
    }

    private static String getChromeDriverVersion(String driverPath) throws Exception {
        Process process = new ProcessBuilder(driverPath, "--version").start();
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        String versionLine = reader.readLine();
        if (versionLine == null || versionLine.isEmpty()) throw new RuntimeException("Cannot detect ChromeDriver version");
        return versionLine.replace("ChromeDriver ", "").trim();
    }
}

