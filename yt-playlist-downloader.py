import sys
import os
import yt_dlp
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QTextEdit,
    QComboBox, QHBoxLayout, QSpinBox, QProgressBar, QMessageBox, QFileDialog, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings, QTimer
from PyQt5.QtGui import QIcon



class PlaylistFetcher(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(list, int)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        options = {
            'extract_flat': True,
            'quiet': True
        }
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(self.url, download=False)
                playlist_info = info.get('entries', [])
                total_videos = len(playlist_info)
                
                for i in range(1, 101):
                    self.progress_signal.emit(i)
                    QThread.msleep(50)
                self.finished_signal.emit(playlist_info, total_videos)
        except Exception as e:
            self.finished_signal.emit([], 0)


class DownloadThread(QThread):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)

    def __init__(self, url, options):
        super().__init__()
        self.url = url
        self.options = options

    def run(self):
        try:
            with yt_dlp.YoutubeDL(self.options) as ydl:
                ydl.add_progress_hook(self.progress_hook)
                self.status_signal.emit("Download started...")
                ydl.download([self.url])
            self.status_signal.emit("Download Complete!")
        except Exception as e:
            self.status_signal.emit(f"Error: {str(e)}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            progress = int(d['downloaded_bytes'] / d['total_bytes'] * 100)
            self.progress_signal.emit(progress)
            self.status_signal.emit(f"Downloading: {d['filename']} ({d['downloaded_bytes'] / (1024 * 1024):.2f} MB)")

        # If the download fails for a video, it will continue with the next one.
        if d['status'] == 'error':
            self.status_signal.emit(f"Error downloading: {d['filename']} (Skipping this video...)")



class YouTubePlaylistDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.playlist_info = []
        self.is_playlist_fetched = False
        self.download_folder = ""

        # Load saved settings
        self.settings = QSettings("MyCompany", "YouTubePlaylistDownloader")
        self.load_last_download_folder()

    def initUI(self):
        self.setWindowTitle("YouTube Playlist Downloader")
        self.setWindowIcon(QIcon('icons/icon.png'))

        layout = QVBoxLayout()
        
        # Playlist URL Section
        self.url_group = QGroupBox("Enter Playlist URL:")
        url_layout = QVBoxLayout()
        self.url_input = QLineEdit(self)
        url_layout.addWidget(self.url_input)
        self.fetch_button = QPushButton("Fetch Playlist Details", self)
        self.fetch_button.clicked.connect(self.fetch_playlist)
        url_layout.addWidget(self.fetch_button)
        self.url_group.setLayout(url_layout)
        layout.addWidget(self.url_group)

        # Playlist Details Section
        self.details_group = QGroupBox("Playlist Details:")
        details_layout = QVBoxLayout()
        self.playlist_details = QTextEdit(self)
        self.playlist_details.setReadOnly(True)
        details_layout.addWidget(self.playlist_details)
        self.fetch_progress_bar = QProgressBar(self)
        self.fetch_progress_bar.setRange(0, 100)
        details_layout.addWidget(self.fetch_progress_bar)
        self.details_group.setLayout(details_layout)
        layout.addWidget(self.details_group)

        # Quality and Range Section
        self.settings_group = QGroupBox("Download Settings:")
        settings_layout = QVBoxLayout()

        self.quality_label = QLabel("Select Video Quality:")
        self.quality_selector = QComboBox(self)
        self.quality_selector.addItems(["Best", "Medium", "Worst"])
        settings_layout.addWidget(self.quality_label)
        settings_layout.addWidget(self.quality_selector)

        range_layout = QHBoxLayout()
        self.range_label = QLabel("Select Range:")
        self.start_range = QSpinBox()
        self.start_range.setRange(1, 1000)
        self.end_range = QSpinBox()
        self.end_range.setRange(1, 1000)
        range_layout.addWidget(self.range_label)
        range_layout.addWidget(QLabel("Start:"))
        range_layout.addWidget(self.start_range)
        range_layout.addWidget(QLabel("End:"))
        range_layout.addWidget(self.end_range)
        settings_layout.addLayout(range_layout)

        self.folder_label = QLabel("Current Download Folder: Not Selected")
        self.choose_folder_button = QPushButton("Choose Download Folder", self)
        self.choose_folder_button.clicked.connect(self.choose_download_folder)
        settings_layout.addWidget(self.folder_label)
        settings_layout.addWidget(self.choose_folder_button)

        self.settings_group.setLayout(settings_layout)
        layout.addWidget(self.settings_group)

        # Download Button and Status Section
        self.download_button = QPushButton("Download Selected Videos", self)
        self.download_button.clicked.connect(self.download_playlist)
        layout.addWidget(self.download_button)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)  # Enable word wrapping
        self.status_label.setFixedHeight(60)  # Fixed height for status label
        self.status_label.setMaximumWidth(550)  # Maximum width to prevent overflow
        layout.addWidget(self.status_label)

        # New download progress bar
        self.download_progress_bar = QProgressBar(self)
        self.download_progress_bar.setRange(0, 100)
        layout.addWidget(self.download_progress_bar)

        self.setLayout(layout)
        self.setGeometry(300, 300, 600, 500)
        self.show()

    def load_last_download_folder(self):
        """Load the last selected download folder from settings."""
        last_folder = self.settings.value("download_folder", "")
        if last_folder and os.path.exists(last_folder):
            self.download_folder = last_folder
            self.folder_label.setText(f"Current Download Folder: {self.download_folder}")

    def choose_download_folder(self):
        """Open a file dialog to select a download folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.download_folder = folder
            self.folder_label.setText(f"Current Download Folder: {self.download_folder}")
            self.settings.setValue("download_folder", self.download_folder)  # Save the selected folder

    def fetch_playlist(self):
        url = self.url_input.text()
        if not url:
            self.show_error("Please enter a URL.")
            return
        
        if not self.is_valid_youtube_playlist_url(url):
            self.show_error("Invalid YouTube Playlist URL.")
            return

        self.fetch_button.setEnabled(False)
        self.status_label.setText("Fetching playlist details...")
        self.fetch_progress_bar.setValue(1)
        QTimer.singleShot(200, self.start_fetch_thread)

    def start_fetch_thread(self):
        url = self.url_input.text()
        self.fetch_thread = PlaylistFetcher(url)
        self.fetch_thread.progress_signal.connect(self.update_progress)
        self.fetch_thread.finished_signal.connect(self.update_playlist_details)
        self.fetch_thread.start()

    def update_progress(self, progress):
        self.fetch_progress_bar.setValue(progress)

    def update_playlist_details(self, playlist_info, total_videos):
        if playlist_info:
            self.playlist_info = playlist_info
            self.is_playlist_fetched = True
            details = "\n".join([f"{i+1}. {entry['title']}" for i, entry in enumerate(self.playlist_info)])
            self.playlist_details.setText(details)
            self.status_label.setText(f"Playlist fetched! Total videos: {total_videos}")
            self.start_range.setValue(1)
            self.start_range.setMinimum(1)
            self.end_range.setValue(total_videos)
            self.end_range.setMaximum(total_videos)
        else:
            self.status_label.setText("Error fetching playlist details.")
        self.fetch_button.setEnabled(True)

    def download_playlist(self):
        if not self.is_playlist_fetched:
            self.show_error("Please fetch the playlist data first.")
            return

        if not self.download_folder:
            self.show_error("Please choose a download folder first.")
            return

        if not os.path.exists(self.download_folder):
            self.show_error("The selected download folder does not exist.")
            return

        # Disable the download button while the download is in progress
        self.download_button.setEnabled(False)

        url = self.url_input.text()
        quality = self.quality_selector.currentText().lower()
        start = self.start_range.value()
        end = self.end_range.value()

        quality_option = self.get_quality_option(quality)
        options = {
            'format': quality_option,
            'outtmpl': os.path.join(self.download_folder, '%(playlist_index)s-%(title)s.%(ext)s'),
            'playlist_items': f'{start}-{end}',
            'restrictfilenames': True,
            'ignoreerrors': True,  # Skip failed downloads
        }

        # Reset the download progress bar to 0
        self.download_progress_bar.setValue(0)

        # Start the download in a separate thread
        self.download_thread = DownloadThread(url, options)
        self.download_thread.progress_signal.connect(self.update_download_progress)
        self.download_thread.status_signal.connect(self.update_download_status)
        self.download_thread.start()

    def update_download_progress(self, progress):
        # Update the download progress bar
        self.download_progress_bar.setValue(progress)

    def update_download_status(self, status):
        # Update the status label with the download status
        self.status_label.setText(status)

        # Re-enable the download button once the download is complete
        if "Complete" in status or "Error" in status:
            self.download_button.setEnabled(True)

    def get_quality_option(self, quality):
        options = {
            "best": 'bestvideo+bestaudio/best',
            "medium": 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            "worst": 'worstvideo+worseaudio/worst'
        }
        return options.get(quality.lower(), 'bestvideo+bestaudio')

    def is_valid_youtube_playlist_url(self, url):
        youtube_playlist_regex = r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/playlist\?list=[\w-]+"
        return bool(re.match(youtube_playlist_regex, url))

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = YouTubePlaylistDownloader()
    sys.exit(app.exec_())
