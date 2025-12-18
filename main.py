import json

def load_settings(filePath='settings.json'):
    with open(filePath, 'r') as f:
        return json.load(f)

def start_pi1():
    pass

if __name__ == "__main__":
    print('Starting app..')
    settings = load_settings()
    threads = []