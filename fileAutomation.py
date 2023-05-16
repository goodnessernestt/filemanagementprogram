import os
from os import scandir, rename
from os.path import splitext, exists, join
from shutil import move
from time import sleep
from datetime import datetime, timedelta

# The "logging" module is used to write log messages to a file or console
import logging

# The "Observer" and "FileSystemEventHandler" classes will be imported from the "watchdog" module
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Folders that i want to be tracked
source_dir = "/Users/waterloo/Downloads"
sound_download_dir = "/Users/waterloo/Desktop/Sound"
music_download_dir = "/Users/waterloo/Desktop/Sound/music"
video_download_dir = "/Users/waterloo/Desktop/Video downloads"
image_download_dir = "/Users/waterloo/Desktop/Image downloads"
document_download_dir = "/Users/waterloo/Desktop/Documents downloads"

# Store the directories in a list for easy iteration later
directories = [source_dir, sound_download_dir, music_download_dir, video_download_dir, image_download_dir, document_download_dir ]

# Check if each directory exists
# If a directory does not exist, log an error message
for directory in directories:
    if not os.path.isdir(directory):
        logging.error(f"{directory} is not a valid directory")

# Define lists of file extensions for different types of files
# These lists are used to identify which files should be moved to which directories
image_extensions = [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw", ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"]
# Video types
video_extensions = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg", ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"]
# Audio types
audio_extensions = [".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"]
# Document types
document_extensions = [".doc", ".docx", ".odt", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"]


def make_unique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    # IF FILE EXISTS, ADDS NUMBER TO THE END OF THE FILENAME
    while exists(f"{dest}/{name}"):
        try:
            name = f"{filename}({str(counter)}){extension}"
            counter += 1
        except Exception as e:
            logging.error(f"Error occured while renamin file {name}: {e}")
            return None

    return name


def move_file(dest, entry, name):
    if exists(f"{dest}/{name}"):
        unique_name = make_unique(dest, name)
        oldName = join(dest, name)
        newName = join(dest, unique_name)
        rename(oldName, newName)
    move(entry, dest)


class MoverHandler(FileSystemEventHandler):
    # THIS FUNCTION WILL RUN WHENEVER THERE IS A CHANGE IN "source_dir"
    # .upper is for not missing out on files with uppercase extensions
    def on_modified(self, event):
        with scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                self.check_audio_files(entry, name)
                self.check_video_files(entry, name)
                self.check_image_files(entry, name)
                self.check_document_files(entry, name)

    def check_audio_files(self, entry, name):  # Checks all Audio Files
        for audio_extension in audio_extensions:
            if name.endswith(audio_extension) or name.endswith(audio_extension.upper()):
                if entry.stat().st_size < 10_000_000 or "SFX" in name:  # ? 10Megabytes
                    dest = sound_download_dir
                else:
                    dest = music_download_dir
                move_file(dest, entry, name)
                logging.info(f"Moved audio file: {name}")

    def check_video_files(self, entry, name):  # Checks all Video Files
        for video_extension in video_extensions:
            if name.endswith(video_extension) or name.endswith(video_extension.upper()):
                move_file(video_download_dir, entry, name)
                logging.info(f"Moved video file: {name}")

    def check_image_files(self, entry, name):  # Checks all Image Files
        for image_extension in image_extensions:
            if name.endswith(image_extension) or name.endswith(image_extension.upper()):
                now = datetime.now()
                two_days_ago = now - timedelta(days=2)
                file_creation_time = datetime.fromtimestamp(entry.stat(). st_ctime)
                if file_creation_time < two_days_ago:  # Modify this condition as needed
                    move_file(image_download_dir + "/old", entry, name)
            else:
                if entry.stat().st_size < 1000000:  # Modify this value as needed
                    move_file(image_download_dir + "/small", entry, name)
                else:
                    move_file(image_download_dir + "/large", entry, name)
                move_file(image_download_dir, entry, name)
                logging.info(f"Moved image file: {name}")

    def check_document_files(self, entry, name):  # Checks all Document Files
        for documents_extension in document_extensions:
            if name.endswith(documents_extension) or name.endswith(documents_extension.upper()):
                move_file(document_download_dir, entry, name)
                logging.info(f"Moved document file: {name}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()