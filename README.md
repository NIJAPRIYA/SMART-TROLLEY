
# AI-Powered Smart Autonomous Shopping Trolley

## Overview

The AI-Powered Smart Autonomous Shopping Trolley is an intelligent retail automation system designed to enhance customer convenience and improve store efficiency. The trolley autonomously follows customers, enables cashier-less shopping through barcode-based billing, and provides machine learning-driven sales analytics for retailers.

---

## Features

###  Human Following System

* Autonomous customer following using computer vision.
* Real-time person detection using **MobileNet SSD v2** pretrained on the **COCO dataset**.
* Bounding box tracking and center-point alignment for navigation.
* Dynamic trolley movement based on customer position.
* Safe-distance maintenance using ultrasonic sensors.

### 🛍 Smart Barcode Billing

* Cashier-less shopping experience.
* Custom **16-digit Code128 barcode system**:

  * First 12 digits → Product ID
  * Last 4 digits → Individual item identifier
* Real-time cart updates through barcode scanning.
* Scan again to remove products from the cart.
* Automatic total bill calculation.

###  Digital Payment Integration

* Dynamic UPI QR code generation for instant payments.
* Queue-free checkout experience.
* QR code generation using Python QRCode library.

###  Sales Analytics & Dynamic Discounts

* Purchase history logging and analytics.
* Product demand analysis based on:

  * Purchase frequency
  * Time of purchase
  * Seasonal trends
  * Product popularity
* Dynamic discount recommendations using **Random Forest** machine learning model.

---

## System Architecture

Customer → Human Detection → Autonomous Following
↓
Barcode Scanning → Cart Management → Billing
↓
Payment via UPI QR Code
↓
Purchase History Database
↓
Machine Learning Analytics → Discount Recommendations

---

## Technology Stack

### Artificial Intelligence & Machine Learning

* MobileNet SSD v2
* Random Forest
* OpenCV
* TensorFlow (pretrained model inference)

### Backend

* Flask
* REST APIs
* JSON Communication

### Database

* SQLite

### Barcode & Payment

* python-barcode
* Code128 Barcode Format
* QRCode Library
* Base64 Encoding

### Hardware

* Raspberry Pi
* Raspberry Pi Camera Module
* Ultrasonic Sensor
* Motor Driver Module
* LED Display

---

## Human Following Workflow

1. Camera continuously captures video frames.
2. MobileNet SSD v2 detects all objects in the frame.
3. Only the **Person** class from the COCO dataset is selected.
4. Bounding box coordinates are extracted.
5. The center of the bounding box is compared with the center of the camera frame.
6. The trolley adjusts direction accordingly.
7. Ultrasonic sensors ensure safe following distance.

---

## Barcode Billing Workflow

1. Retailer generates product barcodes using the barcode generation module.
2. Product information is stored in SQLite.
3. Customer scans a product.
4. Product details are fetched from the database.
5. Item is added to the cart.
6. Rescanning the same item removes it from the cart.
7. Total bill is updated in real time.
8. QR code is generated for payment.

---

## Machine Learning Workflow

1. Purchase data is stored after every transaction.
2. Historical sales trends are analyzed.
3. Random Forest predicts:

   * Slow moving products
   * High demand products
   * Discount recommendations
4. Retailers receive actionable business insights.

---

## Why MobileNet SSD v2?

* Lightweight architecture suitable for Raspberry Pi.
* Real-time inference capability.
* Optimized for embedded systems.
* Faster than traditional object detection models such as Faster R-CNN.
* Provides an ideal balance between speed and accuracy.

---

## Why Random Forest?

* Handles non-linear retail data effectively.
* Reduces overfitting through bagging.
* Requires minimal hyperparameter tuning.
* Performs well on tabular sales datasets.
* Provides feature importance for business insights.

---

## Future Enhancements

* Customer re-identification for multi-customer environments.
* Personalized product recommendations.
* Cloud synchronization for inventory management.
* Mobile application integration.
* Real-time dashboard for retailers.

---

## License

This project is intended for educational, research, and retail automation purposes.
