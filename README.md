Markdown

# 🔍 Lost & Found Finder

## 💡 Project Overview

The **Lost & Found Finder** is a web application designed to help people report lost or found items and connect with the rightful owners.

Think of it as a central digital hub for your community's lost and found. If you find something, you can post it. If you've lost something, you can search for it!

---

## ✨ Key Features

This system makes finding and reporting items simple:

* **User Accounts:** Secure sign-up and login for regular users.
* **Report Found Items:** Users can easily submit details about an item they've found, including its **name, description, location, and date**.
* **Image Search:** You can upload a photo of a found item, and the system uses **image recognition technology** to find similar items already reported!
* **Keyword Search:** Search for lost items using keywords in the name or description (e.g., "blue backpack" or "keys with leather fob").
* **Claiming Items:** If you find an item that matches one you've lost, you can officially **claim it**. The system will then share the contact information of the person who reported it found (the **finder**) so you can arrange the pickup.
* **Administrator Control:** The system has special admin accounts to oversee all items and users.

---

## 🚀 How to Use the Application

### 1. Getting Started

1.  **Sign Up/Register:** You will need a personal account to report or claim items. The first person to sign up will automatically be designated as the **Admin** of the system.
2.  **Log In:** Use your username/email and password to access the full features.

### 2. Found an Item? (Reporting)

1.  Go to the **Report** section.
2.  Fill in all the details about the item you found: what it is, where you found it, and a detailed description.
3.  **Crucially, upload a clear picture** of the item. The better the photo, the easier it is for the owner to find it through the image search.

### 3. Lost an Item? (Searching and Claiming)

1.  Go to the **Search** section.
2.  You have two ways to search:
    * **Text Search:** Enter a descriptive word or phrase (e.g., "red wallet").
    * **Image Search:** Upload a picture of the item you lost (if you have one). The system will check for close image matches.
3.  If you find a matching item:
    * Click on the item to see details.
    * If you are certain it's yours, click the **Claim** button.
    * The system will instantly provide you with the **finder's contact email and username** so you can reach out to them.
    * The item will then be marked as **Claimed** and removed from search results.

---

## 🔒 Security and Privacy Notes

* **Passwords are Secure:** Your password is never stored as plain text. It is scrambled using a high-security method called **scrypt**.
* **Admin Access:** Only users with special **Admin** privileges can view the complete list of all users and reported items for moderation.
* **Contact Privacy:** A finder's contact information (email/username) is **only revealed** to the person who successfully claims the item.

---

## 🛠️ Technical Details (For the Curious)

This application is built using modern web technology:

* **Framework:** **Flask** (a Python-based web framework).
* **Database:** **SQLAlchemy** (used with a simple file-based database called `sqlite:///search.sqlite`) to securely store all user and item data.
* **User Management:** **Flask-Login** handles secure user sessions and login/logout processes.
* **Image Hashing:** The system uses the **imagehash** library (specifically the `average_hash`) to calculate a unique "fingerprint" for every image. This allows it to compare a search image to all reported images and find items that look visually similar.
Would you like me to draft a brief set of instructions for setting up and running this application on a computer, or perhaps suggest some features to add next?
