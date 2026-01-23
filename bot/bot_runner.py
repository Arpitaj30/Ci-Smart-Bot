import requests
import sys
import os

BOT_SERVER = os.getenv("BOT_SERVER_URL", "http://127.0.0.1:8000")

def main():
    log_file = sys.argv[1]
    with open(log_file) as f:
        logs = f.read()

    payload = {
        "logs": logs,
        "repo": os.getenv("GITHUB_REPOSITORY"),
        "pr_number": os.getenv("PR_NUMBER", "0")
    }

    response = requests.post(f"{BOT_SERVER}/analyze", json=payload)
    print(response.json())

if __name__ == "__main__":
    main()



# import requests
# import os

# BOT_SERVER = os.getenv("BOT_SERVER_URL", "http://127.0.0.1:8000")

# def main():
#     with open("ci_logs.txt") as f:
#         logs = f.read()

#     payload = {
#         "logs": logs,
#         "repo": os.getenv("GITHUB_REPOSITORY"),
#         "pr_number": os.getenv("PR_NUMBER", "0")  # SAFE DEFAULT
#     }

#     r = requests.post(f"{BOT_SERVER}/analyze", json=payload)
#     print(r.status_code, r.text)

# if __name__ == "__main__":
#     main()
