package com.example.tiktokcleaner;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

import java.io.FileWriter;
import java.io.IOException;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class TikTokLinkExtractor {

    public static String extractLinks() throws Exception {
        ChromeDriverManager.setupChromeDriver();

        ChromeOptions options = new ChromeOptions();
        options.addArguments("--start-maximized");
        options.addArguments("user-data-dir=/tmp/chrome-profile-" + System.currentTimeMillis());

        WebDriver driver = new ChromeDriver(options);

        driver.get("https://www.tiktok.com/login");
        System.out.println("Log in manually, then press Enter...");
        System.in.read();

        driver.get("https://www.tiktok.com/favorites");
        Thread.sleep(5000);

        long lastHeight = (long) ((org.openqa.selenium.JavascriptExecutor) driver)
                .executeScript("return document.body.scrollHeight");

        while (true) {
            ((org.openqa.selenium.JavascriptExecutor) driver)
                    .executeScript("window.scrollTo(0, document.body.scrollHeight);");
            Thread.sleep(2000);
            long newHeight = (long) ((org.openqa.selenium.JavascriptExecutor) driver)
                    .executeScript("return document.body.scrollHeight");
            if (newHeight == lastHeight) break;
            lastHeight = newHeight;
        }

        List<WebElement> videoElements = driver.findElements(By.xpath("//a[contains(@href, '/video/')]"));
        Set<String> links = new HashSet<>();
        for (WebElement el : videoElements) {
            links.add(el.getAttribute("href"));
        }

        String homeDir = System.getProperty("user.home");
        String filename = homeDir + "/tiktok_saved_links.txt";
        try (FileWriter writer = new FileWriter(filename)) {
            for (String link : links) {
                writer.write(link + "\n");
            }
        }

        driver.quit();
        System.out.println("Extracted " + links.size() + " links. Saved to: " + filename);
        return filename;
    }
}
