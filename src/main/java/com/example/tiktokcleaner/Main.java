package com.example.tiktokcleaner;

public class Main {
    public static void main(String[] args) throws Exception {
        System.out.println("=== TikTok Cleaner Workflow ===");

        String extractedFile = TikTokLinkExtractor.extractLinks();

        String homeDir = System.getProperty("user.home");
        String cleanedFile = homeDir + "/tiktok_valid_links.txt";

        TikTokLinkChecker.checkLinks(extractedFile, cleanedFile);

        System.out.println("\nWorkflow complete!");
        System.out.println("✅ Extracted links: " + extractedFile);
        System.out.println("✅ Valid links: " + cleanedFile);
    }
}
