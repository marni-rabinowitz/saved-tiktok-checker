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
import java.sql.Time;
import java.util.*;

public class TikTokLinkCleaner extends Application {
    private final ObservableList<TikTokLink> links = FXCollections.observableArrayList();
    private TableView<TikTokLink> table;

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage stage) {
        stage.setTitle("TikTok Saved Video Cleaner");

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
            links.clear();
            for (String line : Files.readAllLines(file.toPath())) {
                String url = line.trim();
                if (!url.isEmpty()) links.add(new TikTokLink(url));
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void checkLinks() {
        for (TikTokLink link : links) {
            new Thread(() -> {
                try {
                    int status = Request.get(link.url)
                            .connectTimeout(Timeout.ofSeconds(5))
                            .execute()
                            .returnResponse()
                            .getCode();

                    link.status = (status == 200) ? "✅ Exists" : "❌ Missing (" + status + ")";
                } catch (Exception e) {
                    link.status = "❌ Missing/Error";
                }

                javafx.application.Platform.runLater(() -> table.refresh());
            }).start();
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

    static class TikTokLink {
        String url;
        String status = "⏳ Not checked";

        TikTokLink(String url) {
            this.url = url;
        }
    }
}
