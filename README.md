# YouTube Playlist Downloader  

A simple and lightweight desktop application built with **PyQt5** to download videos from YouTube playlists using `yt_dlp`. The app allows you to fetch playlist details, choose video quality, set a range of videos to download, and select a custom download folder.  

## Features  
- Fetch and display YouTube playlist details.  
- Select video quality: Best, Medium, or Worst.  
- Specify a range of videos to download.  
- Choose a custom download folder for saving files.  

![image](https://github.com/user-attachments/assets/b073f638-4d07-4388-ade5-ac6d77ed886e)

## Installation:
To install the application, 

### For Linux 
download the [.deb package](https://github.com/shamith-perera/Yotube-Playlist-Downloader/releases/download/v1.0.0/yt-playlist-downloader.deb) and install it using `dpkg`(for Debian/Ubuntu-based distributions) :
```
sudo dpkg -i yt-playlist-downloader.deb
sudo apt-get install -f  # To resolve dependencies if needed
```
#### or

download the [.AppImage](https://github.com/shamith-perera/Yotube-Playlist-Downloader/releases/download/v1.0.0/Yt_Playlist_Downloader-x86_64.AppImage) and run it (Portable) :
```
chmod +x Yt_Playlist_Downloader-x86_64.AppImage
./Yt_Playlist_Downloader-x86_64.AppImage
```

### For Windows
download and run the [.exe](https://github.com/shamith-perera/Yotube-Playlist-Downloader/releases/download/v1.0.0/yt-playlist-downloader.exe) file (Portable)



### Running From the Source
you can clone this repository and run the application directly (requires Python 3.x, PyQt5, and yt_dlp):

```
git clone https://github.com/shamith-perera/Yotube-Playlist-Downloader.git
cd Yotube-Playlist-Downloader
pip install -r requirements.txt
python yt-playlist-downloader.py
```
Note: Make sure you have pip installed for Python and the necessary dependencies (PyQt5, yt_dlp).

## Dependencies:
- PyQt5
- yt_dlp

### Acknowledgments
This project uses the following open-source libraries:
- [yt_dlp](https://github.com/yt-dlp/yt-dlp) – for downloading YouTube videos and extracting playlist details.
- PyQt5 – for building the graphical user interface (GUI).

