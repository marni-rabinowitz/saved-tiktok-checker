package com.example.tiktok;
import javafx.application.Application;
import javafx.beans.property.SimpleStringProperty;
import javafx.collections.*;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.TableView;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableCell;
import javafx.scene.layout.*;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import org.apache.hc.client5.http.fluent.Request;
import org.apache.hc.core5.util.Timeout;

import java.awt.*;
import java.io.*;
import java.net.URI;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class TikTokLinkCleaner extends Application {
    private final ObservableList<TikTokLink> links = FXCollections.observableArrayList();
    private TableView<TikTokLink> table;
    private ExecutorService executorService;
    private final AtomicInteger activeRequests = new AtomicInteger(0);

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage stage) {
        // Initialize thread pool with limited threads to prevent resource exhaustion
        executorService = Executors.newFixedThreadPool(5);
        
        stage.setTitle("TikTok Saved Video Cleaner");
        
        // Properly handle application shutdown
        stage.setOnCloseRequest(e -> {
            shutdownExecutorService();
        });

        Button loadBtn = new Button("Load Links");
        Button checkBtn = new Button("Check Links");
        Button saveBtn = new Button("Save Valid Links");

        table = new TableView<>(links);
        TableColumn<TikTokLink, String> urlCol = new TableColumn<>("TikTok URL");
        urlCol.setCellValueFactory(c -> new SimpleStringProperty(c.getValue().url));

        TableColumn<TikTokLink, String> statusCol = new TableColumn<>("Status");
        statusCol.setCellValueFactory(c -> new SimpleStringProperty(c.getValue().status));

        TableColumn<TikTokLink, String> actionCol = new TableColumn<>("Actions");
        actionCol.setCellFactory(col -> new TableCell<>() {
            private final Button openBtn = new Button("Open");

            {
                openBtn.setOnAction(e -> {
                    TikTokLink item = getTableView().getItems().get(getIndex());
                    try {
                        Desktop.getDesktop().browse(URI.create(item.url));
                    } catch (IOException ex) {
                        ex.printStackTrace();
                    }
                });
            }

            @Override
            protected void updateItem(String s, boolean empty) {
                super.updateItem(s, empty);
                if (empty) {
                    setGraphic(null);
                } else {
                    setGraphic(openBtn);
                }
            }
        });

        table.getColumns().addAll(urlCol, statusCol, actionCol);
        table.setColumnResizePolicy(TableView.CONSTRAINED_RESIZE_POLICY);

        loadBtn.setOnAction(e -> loadFile(stage));
        checkBtn.setOnAction(e -> checkLinks());
        saveBtn.setOnAction(e -> saveValidLinks(stage));

        HBox buttons = new HBox(10, loadBtn, checkBtn, saveBtn);
        buttons.setPadding(new Insets(10));

        VBox layout = new VBox(10, buttons, table);
        layout.setPadding(new Insets(10));

        stage.setScene(new Scene(layout, 800, 500));
        stage.show();
    }

    private void loadFile(Stage stage) {
        FileChooser fc = new FileChooser();
        fc.setTitle("Select TikTok Links File");
        fc.getExtensionFilters().add(new FileChooser.ExtensionFilter("Text Files", "*.txt"));
        File file = fc.showOpenDialog(stage);
        if (file == null) return;

        try {
            // Clear existing links to prevent accumulation
            links.clear();
            
            // Use try-with-resources to ensure proper resource cleanup
            try (BufferedReader reader = Files.newBufferedReader(file.toPath())) {
                String line;
                while ((line = reader.readLine()) != null) {
                    String url = line.trim();
                    if (!url.isEmpty()) {
                        links.add(new TikTokLink(url));
                    }
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void checkLinks() {
        // Cancel any existing requests before starting new ones
        if (executorService != null && !executorService.isShutdown()) {
            // Reset active request counter
            activeRequests.set(0);
            
            // Create a list to track futures for proper cleanup
            java.util.List<Future<?>> futures = new ArrayList<>();
            
            for (TikTokLink link : links) {
                // Limit concurrent requests to prevent overwhelming the system
                if (activeRequests.get() >= 10) {
                    try {
                        Thread.sleep(100); // Brief pause to allow some requests to complete
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
                
                Future<?> future = executorService.submit(() -> {
                    activeRequests.incrementAndGet();
                    try {
                        int status = Request.get(link.url)
                                .connectTimeout(Timeout.ofSeconds(5))
                                .responseTimeout(Timeout.ofSeconds(10))
                                .execute()
                                .returnResponse()
                                .getCode();

                        link.status = (status == 200) ? "✅ Exists" : "❌ Missing (" + status + ")";
                    } catch (Exception e) {
                        link.status = "❌ Missing/Error";
                    } finally {
                        activeRequests.decrementAndGet();
                        // Update UI on JavaFX Application Thread
                        javafx.application.Platform.runLater(() -> table.refresh());
                    }
                });
                
                futures.add(future);
            }
        }
    }

    private void saveValidLinks(Stage stage) {
        FileChooser fc = new FileChooser();
        fc.setTitle("Save Cleaned List");
        fc.getExtensionFilters().add(new FileChooser.ExtensionFilter("Text Files", "*.txt"));
        File file = fc.showSaveDialog(stage);
        if (file == null) return;

        try (BufferedWriter writer = Files.newBufferedWriter(file.toPath())) {
            for (TikTokLink link : links) {
                if (link.status.startsWith("✅")) {
                    writer.write(link.url);
                    writer.newLine();
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    /**
     * Properly shutdown the executor service to prevent resource leaks
     */
    private void shutdownExecutorService() {
        if (executorService != null && !executorService.isShutdown()) {
            executorService.shutdown();
            try {
                // Wait for existing tasks to complete
                if (!executorService.awaitTermination(10, TimeUnit.SECONDS)) {
                    // Force shutdown if tasks don't complete within timeout
                    executorService.shutdownNow();
                    // Wait a bit more for tasks to respond to being cancelled
                    if (!executorService.awaitTermination(5, TimeUnit.SECONDS)) {
                        System.err.println("Executor did not terminate gracefully");
                    }
                }
            } catch (InterruptedException e) {
                // Re-interrupt the current thread if interrupted
                Thread.currentThread().interrupt();
                // Force shutdown
                executorService.shutdownNow();
            }
        }
    }

    @Override
    public void stop() throws Exception {
        // Ensure proper cleanup when application stops
        shutdownExecutorService();
        super.stop();
    }

    static class TikTokLink {
        String url;
        String status = "⏳ Not checked";

        TikTokLink(String url) {
            this.url = url;
        }
    }
}
