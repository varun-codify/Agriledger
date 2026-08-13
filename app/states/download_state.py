import datetime
import logging
import zipfile
from pathlib import Path

import reflex as rx


class DownloadState(rx.State):
    """State for handling project downloads."""

    @rx.event
    def create_project_zip(self):
        """Creates a zip file of the project and initiates download."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            zip_filename = f"AgriLedger_Project_{timestamp}.zip"
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            zip_path = upload_dir / zip_filename
            root_dir = Path(".")
            excluded_dirs = {
                "__pycache__",
                ".web",
                "node_modules",
                ".git",
                ".venv",
                "venv",
                "uploaded_files",
                "_upload",
                "assets/tmp",
                ".pytest_cache",
                "reports",
            }
            excluded_extensions = {".pyc", ".pyo", ".pyd", ".DS_Store", ".env", ".zip"}
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in root_dir.rglob("*"):
                    if not file_path.is_file():
                        continue
                    parts = file_path.parts
                    if any((part in excluded_dirs for part in parts)):
                        continue
                    if file_path.suffix in excluded_extensions:
                        continue
                    if file_path.name == zip_filename:
                        continue
                    zipf.write(file_path, arcname=file_path)
            return rx.download(url=f"/_upload/{zip_filename}", filename=zip_filename)
        except Exception as e:
            logging.exception(f"Failed to create project zip: {e}")
            return rx.toast.error(f"Failed to prepare download: {str(e)}")
