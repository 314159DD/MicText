#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::io::{BufRead, BufReader};
use std::process::{Command, Stdio};
use tauri::{AppHandle, Manager};
use tauri::Emitter;
use std::sync::Mutex;
use tauri::Window;

// Store the current process handle
struct TranscriptionState {
    process: Option<std::process::Child>,
}

impl Default for TranscriptionState {
    fn default() -> Self {
        Self { process: None }
    }
}

#[tauri::command]
fn send_notification(window: Window, message: String) -> Result<(), String> {
    window.emit("notification", message).map_err(|e| e.to_string())
}

#[tauri::command]
fn start_recording(app: AppHandle, service: String) -> String {
    println!("Starting recording with service: {}", service);
    
    // Get the state
    let state = app.state::<Mutex<TranscriptionState>>();
    let mut state = state.lock().unwrap();
    
    // Kill any existing process
    if let Some(mut process) = state.process.take() {
        let _ = process.kill();
        // Emit a notification that previous process was stopped
        if let Some(window) = app.get_webview_window("main") {
             let _ = window.emit("notification", "Stopping previous transcription...".to_string());
        }
    }

    // Choose the script based on service
    let script = match service.as_str() {
        "whisper" => {
            // Emit a notification for starting Whisper
            if let Some(window) = app.get_webview_window("main") {
                 let _ = window.emit("notification", "Starting Whisper transcription...".to_string());
            }
            "transcribe.py"
        },
        "google" => {
            // Emit a notification for starting Google
            if let Some(window) = app.get_webview_window("main") {
                 let _ = window.emit("notification", "Starting Google transcription...".to_string());
            }
            "gloud_transcribe.py"
        },
        _ => return "Invalid service selected".to_string(),
    };

    // Start the new process
    let mut child = Command::new("python")
        .arg(script)
        .stdout(Stdio::piped())
        // Set GOOGLE_APPLICATION_CREDENTIALS for google service using the absolute path
        .envs(if service == "google" { 
            vec![("GOOGLE_APPLICATION_CREDENTIALS", "C:\\Coding\\II____Projects\\MicText\\gcloud-key.json")] 
        } else { 
            vec![] 
        })
        .spawn()
        .expect("Failed to start transcription script");

    // Take stdout before moving child into state
    let stdout = child.stdout.take();
    
    // Store the process handle
    state.process = Some(child);

    // Start reading the output in a separate thread if we have stdout
    if let Some(stdout) = stdout {
        let window = app.get_webview_window("main").expect("main window not found");
        std::thread::spawn(move || {
            let reader = BufReader::new(stdout);
            for line in reader.lines() {
                if let Ok(text) = line {
                    window.emit("transcript", text).unwrap();
                }
            }
        });
    }

    format!("Started {} transcription", service)
}

#[tauri::command]
fn stop_transcription(app: AppHandle) -> String {
    let state = app.state::<Mutex<TranscriptionState>>();
    let mut state = state.lock().unwrap();
    
    if let Some(mut process) = state.process.take() {
        let _ = process.kill();
        // Emit a notification for stopping
        if let Some(window) = app.get_webview_window("main") {
             let _ = window.emit("notification", "Transcription stopped.".to_string());
        }
        "Transcription stopped".to_string()
    } else {
        "No transcription running".to_string()
    }
}

fn main() {
    tauri::Builder::default()
        .manage(Mutex::new(TranscriptionState::default()))
        .invoke_handler(tauri::generate_handler![start_recording, stop_transcription, send_notification])
        .run(tauri::generate_context!())
        .expect("error while running tauri app");
}
