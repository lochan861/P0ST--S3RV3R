import requests  # For making HTTP requests
import json      # For handling JSON responses
import time      # For time-related functions
import os        # For interacting with the operating system
import re        # For regular expressions
import random    # For selecting random items
import threading
from requests.exceptions import RequestException, ConnectionError  # For error handling in HTTP requests
from http.server import SimpleHTTPRequestHandler  # For creating a simple HTTP server
import socketserver  # For socket server to run the HTTP server

# Define color constants
GREEN = "\033[1;32;1m"
RED = "\033[1;31;1m"
CYAN = "\033[1;36;1m"
RESET = "\033[0m"

# Custom HTTP request handler
class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"S3RV3R IS RUNN1NG")

def execute_server():
    PORT = int(os.getenv('PORT', 8080))
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        httpd.serve_forever()

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def read_file(file_path):
    """Read data from a file and return a list of stripped lines."""
    if not os.path.isfile(file_path):
        print(f"{RED}[!] File not found: {file_path}. Skipping...")
        return None
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def validate_token(token):
    """Validate token and return user/page name if valid."""
    try:
        response = requests.get(f'https://graph.facebook.com/me?access_token={token}')
        if response.status_code == 200:
            profile_data = response.json()
            print(f"{GREEN}[✓] Valid Profile Token: {profile_data.get('name')}")
            return "profile", profile_data.get("name")

        response = requests.get(f'https://graph.facebook.com?access_token={token}')
        if response.status_code == 200:
            page_data = response.json()
            if "name" in page_data:
                print(f"{GREEN}[✓] Valid Page Token: {page_data['name']}")
                return "page", page_data["name"]

        print(f"{RED}[!] Invalid Token")
        return None, None
    except RequestException:
        print(f"{RED}[!] Error validating token")
        return None, None

def get_valid_tokens(token_file):
    """Validate all tokens from the file."""
    tokens = read_file(token_file)
    if not tokens:
        return []

    valid_tokens = []
    for index, token in enumerate(tokens, start=1):
        token_type, name = validate_token(token)
        if name:
            valid_tokens.append((index, token_type, name, token))  # Add token number

    return valid_tokens

def main():
    cls()  # Clear screen
    print(f"{GREEN} || Tool Start Time ||: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Load data from files
    token_file = "tokennum.txt"
    comment_file = "Comments.txt"
    time_file = "time.txt"
    firstname_file = "firstname.txt"
    lastname_file = "lastname.txt"
    postuid_file = "postuid.txt"

    valid_tokens = get_valid_tokens(token_file)
    if not valid_tokens:
        print(f"{RED}[!] No valid tokens found. Exiting...")
        return

    comments = read_file(comment_file)
    post_ids = read_file(postuid_file)
    time_values = read_file(time_file)

    # Make first and last names optional
    first_names = read_file(firstname_file) or []
    last_names = read_file(lastname_file) or []

    if not (comments and post_ids and time_values):
        print(f"{RED}[!] Missing required files (Comments, Post UIDs, or Time settings). Exiting...")
        return

    delay = int(time_values[0])
    if delay < 60:
        print(f"{RED}[!] Delay too short. Setting minimum delay of 60 seconds.")
        delay = 60

    print(f"{GREEN}[✓] Ready to start sending comments!")

    comment_index = 0
    token_index = 0
    comment_number = 1  # Initialize comment counter

    while True:
        try:
            comment = comments[comment_index]
            post_id = random.choice(post_ids)
            token_num, profile_type, profile_name, current_token = valid_tokens[token_index]

            # Add first and last names only if available
            first_name = random.choice(first_names) if first_names else ""
            last_name = random.choice(last_names) if last_names else ""

            # Ensure spaces between names and comment
            formatted_comment = " ".join(filter(None, [first_name, comment, last_name]))

            print(f"\n{CYAN}=======================================")
            print(f"{CYAN}[✓] Comment #{comment_number} using Token #{token_num}")
            print(f"{CYAN}Profile/Page :: {profile_name} ({profile_type.upper()})")
            print(f"{CYAN}Post ID :: {post_id}")
            print(f"{CYAN}Comment :: {formatted_comment}")
            print(f"{CYAN}=======================================\n")

            response = requests.post(f'https://graph.facebook.com/{post_id}/comments/',
                                     data={'message': formatted_comment, 'access_token': current_token}).json()

            if 'id' in response:
                print(f"{GREEN}[✓] Comment sent successfully!")
                comment_number += 1  # Increment comment counter
                time.sleep(delay)
            else:
                error_message = response.get('error', {}).get('message', 'Unknown error')
                print(f"{RED}[!] Failed to comment: {error_message}")

            token_index = (token_index + 1) % len(valid_tokens)
            comment_index = (comment_index + 1) % len(comments)

        except RequestException as e:
            print(f"{RED}[!] Error making request: {e}")
            time.sleep(5)

if __name__ == "__main__":
    server_thread = threading.Thread(target=execute_server)
    server_thread.daemon = True
    server_thread.start()

    main()
