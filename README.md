# Tauri + Vanilla

This template should help get you started developing with Tauri in vanilla HTML, CSS and Javascript.

## Recommended IDE Setup

- [VS Code](https://code.visualstudio.com/) + [Tauri](https://marketplace.visualstudio.com/items?itemName=tauri-apps.tauri-vscode) + [rust-analyzer](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer)

## Setup

### Google Cloud Credentials

This project requires Google Cloud credentials to run. To set up your credentials:

1. Go to the [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the necessary APIs for your project
4. Create a service account and download the credentials JSON file
5. Rename the downloaded file to `gcloud-key.json` and place it in the project root directory
6. Make sure to add `gcloud-key.json` to your `.gitignore` file to keep your credentials secure

You can use `gcloud-key.example.json` as a template to see the required structure of the credentials file.
