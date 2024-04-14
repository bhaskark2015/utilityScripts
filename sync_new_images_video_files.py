from ftplib import FTP
import os
from datetime import datetime


def download_files_from_ftp(server, port, username, password, remote_folder, local_destination, cutoff_start_date,
                            cutoff_end_date):
    # Connect to the FTP server
    ftp = FTP()
    ftp.connect(server, port)
    ftp.login(username, password)

    # Change to the specified remote folder
    ftp.cwd(remote_folder)

    # List all files in the remote folder
    files = ftp.nlst()

    for file in files:
        # Get the last modification time of the file on the server
        timestamp = ftp.voidcmd("MDTM " + file)[4:].strip()

        # Parse the timestamp, including milliseconds
        file_datetime = datetime.strptime(timestamp, "%Y%m%d%H%M%S.%f")

        # Check if the file modification date is within the specified range
        if cutoff_start_date <= file_datetime <= cutoff_end_date:
            # Download only files with extensions .jpg, .jpeg, .png, .mp4, .avi, etc.
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.mp4', '.avi')):
                # Create subfolders based on the year, month, and day
                year_month_folder = os.path.join(local_destination, file_datetime.strftime("%Y"),
                                                 file_datetime.strftime("%B"))

                # Create the subfolders if they don't exist
                os.makedirs(year_month_folder, exist_ok=True)

                # Download the file to a temporary location
                temp_file_path = os.path.join(year_month_folder, f"{file}.temp")

                # Check if the file already exists in the destination
                local_file_path = os.path.join(year_month_folder, file)
                if os.path.exists(local_file_path):
                    # If the file already exists, check if it has the same size
                    remote_size = ftp.size(file)
                    local_size = os.path.getsize(local_file_path)

                    if remote_size == local_size:
                        print(f"File {file} already exists in the destination with the same size. Skipping download.")
                        continue
                    else:
                        print(
                            f"File {file} already exists in the destination but with a different size. Deleting the existing file.")

                        # Delete the existing file
                        os.remove(local_file_path)

                print(f"Downloading {file} to {year_month_folder}...")
                with open(temp_file_path, 'wb') as temp_file:
                    ftp.retrbinary('RETR ' + file, temp_file.write)

                # If the download is successful, move the file to its final destination
                remote_size = ftp.size(file)
                local_size = os.path.getsize(temp_file_path)

                # If sizes match, move the file to its final destination
                if remote_size == local_size:
                    final_file_path = os.path.join(year_month_folder, file)
                    os.rename(temp_file_path, final_file_path)
                    print(f"Download of {file} successful.")
                else:
                    print(f"Download of {file} failed. Removing incomplete file.")
                    os.remove(temp_file_path)
        else:
            print(f"Skipping file {file} outside the specified date range.")

    # Close the FTP connection
    ftp.quit()


if __name__ == "__main__":
    # Replace the following variables with y our FTP server credentials and paths
    ftp_server = '192.168.1.68'
    ftp_port = 3230
    ftp_username = 'pc'
    ftp_password = '203690'
    remote_folder_path = 'device/DCIM/Camera/'
    local_destination_path = r'D:\pictures'
    cutoff_start_date = datetime(2024, 1, 1)  # Replace with your cutoff start date
    cutoff_end_date = datetime(2025, 4, 30)  # Replace with your cutoff end date

    # Download files from FTP server to local destination
    download_files_from_ftp(ftp_server, ftp_port, ftp_username, ftp_password, remote_folder_path,
                            local_destination_path, cutoff_start_date, cutoff_end_date)
