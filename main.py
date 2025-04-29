import sys
import os
import requests
import json
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QWidget, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class EmotionDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emotion Detection App (Face++ API)")
        self.setGeometry(100, 100, 800, 600)

        # Face++ API Configuration
        self.api_key = "DoDpfa0TUbdJNH0imIhdii-EZvyA_Bi3"  # Replace with your actual API key
        self.api_secret = "n4gmt456Vdxut1PP-lKj4vGbtLB86OSB"  # Replace with your actual secret
        self.api_url = "https://api-us.faceplusplus.com/facepp/v3/detect"

        self.init_ui()
        self.apply_dark_theme()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.image_label = QLabel("No image uploaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 2px dashed #4C566A; padding: 10px; color: white;")
        self.layout.addWidget(self.image_label, stretch=1)

        self.result_label = QLabel("Emotion: None")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("color: white;")
        self.layout.addWidget(self.result_label)

        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.upload_button = QPushButton("Upload Image")
        self.upload_button.clicked.connect(self.upload_image)
        self.button_layout.addWidget(self.upload_button)

        self.save_button = QPushButton("Save Result")
        self.save_button.clicked.connect(self.save_result)
        self.save_button.setEnabled(False)
        self.button_layout.addWidget(self.save_button)

        self.image_path = None
        self.emotion_result = None
        self.detailed_emotions = None

    def apply_dark_theme(self):
        dark_style = """
            QMainWindow {
                background-color: #2E3440;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #4C566A;
                color: #D8DEE9;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
            QLabel {
                font-size: 16px;
                color: #FFFFFF;
            }
        """
        self.setStyleSheet(dark_style)

    def upload_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select an Image", "", "Images (*.png *.jpg *.jpeg);;All Files (*)", options=options
        )
        if file_path:
            self.image_path = file_path
            self.display_image(file_path)
            self.analyze_emotion(file_path)
        else:
            self.image_label.setText("No image selected")

    def display_image(self, file_path):
        pixmap = QPixmap(file_path)
        self.image_label.setPixmap(pixmap.scaled(
            self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

    def analyze_emotion(self, file_path):
        try:
            with open(file_path, "rb") as image_file:
                image_data = image_file.read()

            params = {
                "api_key": self.api_key,
                "api_secret": self.api_secret,
                "return_attributes": "emotion"
            }
            response = requests.post(self.api_url, data=params, files={"image_file": image_data})

            if response.status_code != 200:
                raise Exception(f"Face++ API Error: {response.status_code} {response.text}")

            result = response.json()
            if "faces" not in result or not result["faces"]:
                self.result_label.setText("No face detected in the image.")
                self.save_button.setEnabled(False)
                return

            emotions = result["faces"][0]["attributes"]["emotion"]
            dominant_emotion = max(emotions, key=emotions.get)


            self.emotion_result = (dominant_emotion, emotions[dominant_emotion])
            self.result_label.setText(f"Detected Emotion: {dominant_emotion}")

            self.detailed_emotions = emotions
            self.save_button.setEnabled(True)

        except Exception as e:
            self.result_label.setText(f"Error: {str(e)}")
            self.save_button.setEnabled(False)

    def save_result(self):
        if self.image_path and self.emotion_result and self.detailed_emotions:
            file_name = "emotion_results.csv"
            columns = ['Image', 'Emotion']

            try:
                if not os.path.exists(file_name) or os.path.getsize(file_name) == 0:
                    pd.DataFrame(columns=columns).to_csv(file_name, index=False)

                new_row = pd.DataFrame([{
                    'Image': os.path.basename(self.image_path),
                    'Emotion': self.emotion_result[0],
                }])

                new_row.to_csv(file_name, mode='a', header=False, index=False)
                self.result_label.setText("Result saved successfully!")
            except Exception as e:
                self.result_label.setText(f"Save error: {str(e)}")
        else:
            self.result_label.setText("No result to save!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmotionDetectionApp()
    window.show()
    sys.exit(app.exec_())
