# command is: python manage.py bir

import os
import time
import zipfile
import csv
import logging
import shutil  # Added to enable directory deletion
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from apps.iPM.models import Data
from django.db import transaction

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory to monitor
directory_to_watch = '/var/sftp/ipm'

class Command(BaseCommand):
    help = 'Processes zip files, extracts CSV files, and updates the database.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting ZIP file processing...'))
        # Process directories immediately under directory_to_watch
        top_level_dirs = [d for d in os.listdir(directory_to_watch) if os.path.isdir(os.path.join(directory_to_watch, d))]
        dir_files_flags = {}
        if top_level_dirs:
            for dir_name in top_level_dirs:
                dir_path = os.path.join(directory_to_watch, dir_name)
                dir_found_files = self.process_directory(dir_path, level=0)
                dir_files_flags[dir_path] = dir_found_files
            if len(top_level_dirs) >= 2:
                for dir_path, has_files in dir_files_flags.items():
                    if not has_files:
                        logger.info(f"Deleting folder without files: {dir_path}")
                        shutil.rmtree(dir_path)
        else:
            # No subdirectories, process directory_to_watch directly
            self.process_directory(directory_to_watch, level=0)

    def process_directory(self, current_dir, level=0):
        """
        Process ZIP files in the current directory, and recursively process subdirectories.
        Delete subfolders that don't contain files (zip and/or csv) based on the specified rules.
        Return True if any files (zip or csv) were found in this directory or subdirectories.
        """
        found_files = False

        # Process files in the current directory
        files_and_dirs = os.listdir(current_dir)
        files = [f for f in files_and_dirs if os.path.isfile(os.path.join(current_dir, f))]
        for filename in files:
            file_path = os.path.join(current_dir, filename)
            found_files = True  # Set to True since we have found a file
            if zipfile.is_zipfile(file_path):
                file_mtime = os.path.getmtime(file_path)
                # Check if the file was last modified more than 1 minute ago
                if time.time() - file_mtime > 60:
                    if self.process_zip(file_path):
                        logger.info(f"ZIP file processed: {filename}")
                    else:
                        logger.error(f"Failed to process ZIP: {filename}")
                        continue  # Retry in the next loop if the ZIP processing fails
                else:
                    logger.info(f"Skipping ZIP file (recently modified): {filename}")
                    # Since the ZIP file is still uploading, we should not delete this directory
            elif filename.endswith('.csv'):
                # Set found_files to True for CSV files as well
                found_files = True
                # Optionally process standalone CSV files
                # If you process them, you can call process_csv here
                # For example:
                # if self.process_csv(file_path):
                #     os.remove(file_path)  # Delete CSV after successful processing
                #     logger.info(f"CSV file successfully processed and deleted: {filename}")
                # else:
                #     logger.error(f"Failed to process CSV: {filename}")
            else:
                # Other files
                found_files = True

        # Process subdirectories
        subdirs = [d for d in files_and_dirs if os.path.isdir(os.path.join(current_dir, d))]
        subdir_files_flags = {}
        for subdir in subdirs:
            subdir_path = os.path.join(current_dir, subdir)
            subdir_found_files = self.process_directory(subdir_path, level=level+1)
            subdir_files_flags[subdir_path] = subdir_found_files

        # Update found_files based on subdirectories
        if any(subdir_files_flags.values()):
            found_files = True

        # After processing subdirectories, check if any subdirectories should be deleted
        if len(subdirs) >= 2:
            for subdir_path, has_files in subdir_files_flags.items():
                if not has_files:
                    # Delete subdirectory if it has no files
                    logger.info(f"Deleting subfolder without files: {subdir_path}")
                    shutil.rmtree(subdir_path)
        # else:
        #   Only one subdir exists; do not delete even if it doesn't have files

        return found_files

    def process_csv(self, file_path):
        """
        Process a CSV file and save its data into the database.
        If the same record (name and time) already exists, update it.
        """
        try:
            logger.info(f"Processing CSV: {file_path}")
            with open(file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                headers = reader.fieldnames
                if headers[0].startswith('\ufeff'):
                    headers[0] = headers[0].replace('\ufeff', '')

                logger.info(f"CSV headers after BOM removal: {headers}")

                for row in reader:
                    row = {k.strip(): v for k, v in row.items()}
                    name = row['MOEntity']
                    inbound_rate = row['Inbound Rate(bit/s)']
                    outbound_rate = row['Outbound Rate(bit/s)']
                    time_str = row['Time']

                    # Parse the naive datetime
                    time_obj = datetime.strptime(time_str, '%m/%d/%Y %H:%M:%S')

                    with transaction.atomic():
                        data, created = Data.objects.update_or_create(
                            name=name,
                            time=time_obj,
                            defaults={
                                'inbound_rate': inbound_rate,
                                'outbound_rate': outbound_rate
                            }
                        )
                        if created:
                            logger.info(f"New record created: {data}")
                        else:
                            logger.info(f"Existing record updated: {data}")
            return True
        except Exception as e:
            logger.error(f"Error processing CSV {file_path}: {e}")
            return False

    def process_zip(self, file_path):
        """
        Extract a ZIP file, process all CSV files inside, and delete the ZIP.
        """
        try:
            logger.info(f"Extracting ZIP file: {file_path}")
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(file_path))  # Extract all files in the current directory
                extracted_files = zip_ref.namelist()
            os.remove(file_path)  # Delete ZIP after extraction
            logger.info(f"ZIP file deleted: {file_path}")

            # After extraction, process the extracted CSV files
            for extracted_file in extracted_files:
                extracted_file_path = os.path.join(os.path.dirname(file_path), extracted_file)
                if os.path.isfile(extracted_file_path) and extracted_file.endswith('.csv'):
                    # Process the CSV file
                    retry_count = 0  # Initialize retry counter
                    max_retries = 10  # Maximum number of retries

                    while retry_count < max_retries:
                        if self.process_csv(extracted_file_path):
                            os.remove(extracted_file_path)  # Delete CSV after successful processing
                            logger.info(f"CSV file successfully processed and deleted: {extracted_file}")
                            break  # Exit the loop once the CSV is processed successfully
                        else:
                            retry_count += 1
                            logger.error(f"Failed to process CSV: {extracted_file}. Retrying ({retry_count}/{max_retries})...")
                            time.sleep(10)  # Sleep for 10 seconds before retrying

                    if retry_count >= max_retries:
                        logger.error(f"CSV processing failed after {max_retries} attempts: {extracted_file}")

                        # Re-zip the CSV file
                        try:
                            # Define the name and path for the new ZIP file
                            zip_file_name = extracted_file + '.zip'  # New ZIP file name
                            zip_file_path = os.path.join(os.path.dirname(extracted_file_path), zip_file_name)

                            # Create a new ZIP file containing the failed CSV file
                            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                zipf.write(extracted_file_path, arcname=extracted_file)  # Use original file name inside ZIP

                            # Delete the CSV file after zipping
                            os.remove(extracted_file_path)
                            logger.info(f"CSV file re-zipped and CSV deleted: {zip_file_path}")
                        except Exception as e:
                            logger.error(f"Failed to re-zip CSV file: {extracted_file_path}. Error: {e}")
                            # Optionally, you can decide whether to keep or remove the CSV in case of failure

            return True
        except Exception as e:
            logger.error(f"Error processing ZIP file {file_path}: {e}")
            return False