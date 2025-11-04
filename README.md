# TikTok Link Cleaner

A simple JavaFX desktop tool that cleans and simplifies TikTok URLs by removing unnecessary tracking parameters and resolving short links. Built with **Java 11**, **JavaFX**, and **Apache HttpClient 5**.

---

## 🚀 Features

* Clean TikTok URLs by removing tracking or referral parameters
* Resolve shortened TikTok links to their canonical form
* Minimal, user-friendly JavaFX interface
* Lightweight and portable (no database required)

---

## 🧰 Tech Stack

* **Java** 11+
* **JavaFX** (for the GUI)
* **Apache HttpClient 5** (for HTTP requests)
* **Maven** (for build and dependency management)

---

## 🗂️ Project Structure

```
tiktok-link-cleaner/
├── pom.xml
└── src/
    └── main/
        ├── java/
        │   └── com/example/tiktok/
        │       └── TikTokLinkCleaner.java
        └── resources/
```

---

## ⚙️ Setup & Installation

### Prerequisites

* JDK 17 or newer
* Maven 3.6+
* Internet connection for dependency resolution

### Setting Up Java 17 on Mac Locally
* run brew install openjdk@17
* run sudo ln -sfn $(brew --prefix openjdk@17)/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk
* run export JAVA_HOME=$(/usr/libexec/java_home -v 17)
* run export PATH=$JAVA_HOME/bin:$PATH

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/tiktok-link-cleaner.git
   cd tiktok-link-cleaner
   ```
2. Build the project:

   ```bash
   mvn clean package
   ```
3. Run the application:

   ```bash
   mvn javafx:run
   ```

---

## 🖥️ Usage

1. Launch the app.
2. Paste a TikTok URL (e.g., a shortened or tracking URL).
3. Click **“Clean”**.
4. Copy or open the cleaned, simplified link directly.

---

## 📦 Dependencies

Defined in [`pom.xml`](pom.xml):

* `org.openjfx:javafx-controls`
* `org.openjfx:javafx-graphics`
* `org.openjfx:javafx-base`
* `org.apache.httpcomponents.client5:httpclient5`
* `org.apache.httpcomponents.client5:httpclient5-fluent`

---

## 🧑‍💻 Development Notes

* Main class: `com.example.tiktok.TikTokLinkCleaner`
* Built and tested with **JavaFX 20**
* Compatible with **OpenJDK 11+**

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

---

## ❤️ Acknowledgements

* [Apache HttpComponents](https://hc.apache.org/httpcomponents-client-5.2.x/)
* [OpenJFX](https://openjfx.io/)
* Inspired by the need to quickly clean TikTok share links for easier sharing.

---

**Author:** Marni Rabinowitz
**Version:** 1.0-SNAPSHOT
