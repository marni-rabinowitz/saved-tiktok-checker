package com.example.tiktokcleaner;

import org.apache.hc.client5.http.classic.methods.HttpHead;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;

import java.io.*;
import java.util.ArrayList;
import java.util.List;

public class TikTokLinkChecker {

    public static void checkLinks(String inputFile, String outputFile) throws IOException {
        List<String> validLinks = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(new FileReader(inputFile));
             FileWriter writer = new FileWriter(outputFile)) {

            String line;
            CloseableHttpClient client = HttpClients.createDefault();

            while ((line = reader.readLine()) != null) {
                try {
                    HttpHead request = new HttpHead(line);
                    int status = client.execute(request).getCode();
                    if (status == 200) {
                        validLinks.add(line);
                        writer.write(line + "\n");
                    }
                } catch (Exception e) {
                    // Skip broken links
                }
            }

            client.close();
        }

        System.out.println("Checked links. Valid links: " + validLinks.size());
    }
}
