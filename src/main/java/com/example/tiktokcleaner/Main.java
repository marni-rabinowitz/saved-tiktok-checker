package com.example.tiktokcleaner;
import org.openqa.selenium.WebDriver;
import java.time.Duration;
import java.util.List;

public class Main {
public static void main(String[] args) {
String userDataDir = System.getenv("TIKTOK_USER_DATA_DIR");
String profileDir = System.getenv("TIKTOK_PROFILE_DIR");
String debuggerAddress = System.getenv("TIKTOK_DEBUGGER_ADDRESS");

WebDriver driver = null;
try {
if (userDataDir != null && !userDataDir.isEmpty()) {
System.out.println("Starting Chrome with existing user profile...");
driver = ChromeDriverManager.createWithUserProfile(userDataDir, profileDir == null ? "Default" : profileDir);
} else if (debuggerAddress != null && !debuggerAddress.isEmpty()) {
System.out.println("Attaching to remote-debugging Chrome...");
driver = ChromeDriverManager.attachToDebuggingChrome(debuggerAddress);
} else {
System.out.println("Starting a visible Chrome instance. Please log in manually.");
driver = ChromeDriverManager.createStandardDriver();
}

driver.get("https://www.tiktok.com/login");

TikTokLinkExtractor extractor = new TikTokLinkExtractor(driver);
extractor.waitForLoginToComplete(Duration.ofSeconds(180));

driver.get("https://www.tiktok.com/foryou");
List<String> links = extractor.extractVideoLinksFromCurrentPage();

System.out.println("Found " + links.size() + " links:");
for (String l : links) System.out.println(l);

} catch (Exception e) {
e.printStackTrace();
} finally {
if (driver != null) {
try { Thread.sleep(2000); } catch (InterruptedException ignored) {}
driver.quit();
}
}
}
}