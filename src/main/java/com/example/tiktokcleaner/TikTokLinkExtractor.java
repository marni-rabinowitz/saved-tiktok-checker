package com.example.tiktokcleaner;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.By;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.support.ui.WebDriverWait;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.nio.file.Files;
import java.nio.file.Path;

public class TikTokLinkExtractor {
private final WebDriver driver;

public TikTokLinkExtractor(WebDriver driver) {
this.driver = driver;
}

public void waitForLoginToComplete(Duration timeout) throws Exception {
WebDriverWait wait = new WebDriverWait(driver, timeout);
try {
wait.until(d -> !d.getCurrentUrl().contains("/login"));
} catch (TimeoutException ex) {
saveDebugArtifacts();
throw new Exception("Login did not complete within " + timeout.getSeconds() + " seconds. Debug artifacts saved.");
}
}

private void saveDebugArtifacts() {
try {
Path outDir = Path.of(System.getProperty("user.home"), "tiktok_debug");
Files.createDirectories(outDir);
if (driver instanceof TakesScreenshot) {
byte[] screenshot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES);
Files.write(outDir.resolve("login_screenshot.png"), screenshot);
}
Files.writeString(outDir.resolve("page_source.html"), driver.getPageSource());
System.err.println("Saved debug artifacts to: " + outDir.toAbsolutePath());
} catch (Exception e) {
System.err.println("Failed to save debug artifacts: " + e.getMessage());
}
}

public List<String> extractVideoLinksFromCurrentPage() {
List<String> links = new ArrayList<>();
List<WebElement> anchors = driver.findElements(By.cssSelector("a[href*='/@'], a[href*='/video/']"));
for (WebElement a : anchors) {
String href = a.getAttribute("href");
if (href != null && !href.isBlank()) links.add(href);
}
return links;
}
}