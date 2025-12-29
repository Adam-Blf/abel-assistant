#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::Serialize;
use std::process::Command;
use std::sync::atomic::{AtomicBool, Ordering};
use tauri::Emitter;

static IS_RUNNING: AtomicBool = AtomicBool::new(false);

#[derive(Clone, Serialize)]
struct LogEvent {
    message: String,
    level: String,
    timestamp: String,
}

#[derive(Clone, Serialize)]
struct StatusEvent {
    running: bool,
    starting: bool,
}

fn get_timestamp() -> String {
    chrono::Local::now().format("%H:%M:%S.%3f").to_string()
}

fn get_project_dir() -> String {
    std::env::current_exe()
        .ok()
        .and_then(|p| p.parent().map(|p| p.to_path_buf()))
        .and_then(|p| p.parent().map(|p| p.to_path_buf()))
        .and_then(|p| p.parent().map(|p| p.to_path_buf()))
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_else(|| ".".to_string())
}

#[tauri::command]
async fn check_docker() -> Result<bool, String> {
    let output = Command::new("docker")
        .arg("info")
        .output()
        .map_err(|e| e.to_string())?;

    Ok(output.status.success())
}

#[tauri::command]
async fn check_status(app: tauri::AppHandle) -> Result<bool, String> {
    let project_dir = get_project_dir();

    let output = Command::new("docker-compose")
        .args(["ps", "-q"])
        .current_dir(&project_dir)
        .output()
        .map_err(|e| e.to_string())?;

    let running = !String::from_utf8_lossy(&output.stdout).trim().is_empty();
    IS_RUNNING.store(running, Ordering::SeqCst);

    Ok(running)
}

#[tauri::command]
async fn start_services(app: tauri::AppHandle) -> Result<(), String> {
    let project_dir = get_project_dir();

    // Emit starting status
    app.emit("status", StatusEvent { running: false, starting: true }).ok();
    app.emit("log", LogEvent {
        message: "INITIATING BOOT SEQUENCE...".to_string(),
        level: "info".to_string(),
        timestamp: get_timestamp(),
    }).ok();

    let output = Command::new("docker-compose")
        .args(["up", "-d", "--build"])
        .current_dir(&project_dir)
        .output()
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        IS_RUNNING.store(true, Ordering::SeqCst);
        app.emit("log", LogEvent {
            message: "ALL SYSTEMS OPERATIONAL - A.B.E.L. ONLINE".to_string(),
            level: "success".to_string(),
            timestamp: get_timestamp(),
        }).ok();
        app.emit("status", StatusEvent { running: true, starting: false }).ok();
    } else {
        let error = String::from_utf8_lossy(&output.stderr);
        app.emit("log", LogEvent {
            message: format!("BOOT SEQUENCE FAILED: {}", error),
            level: "error".to_string(),
            timestamp: get_timestamp(),
        }).ok();
        app.emit("status", StatusEvent { running: false, starting: false }).ok();
    }

    Ok(())
}

#[tauri::command]
async fn stop_services(app: tauri::AppHandle) -> Result<(), String> {
    let project_dir = get_project_dir();

    app.emit("status", StatusEvent { running: true, starting: true }).ok();
    app.emit("log", LogEvent {
        message: "INITIATING SHUTDOWN SEQUENCE...".to_string(),
        level: "warning".to_string(),
        timestamp: get_timestamp(),
    }).ok();

    let output = Command::new("docker-compose")
        .args(["down"])
        .current_dir(&project_dir)
        .output()
        .map_err(|e| e.to_string())?;

    IS_RUNNING.store(false, Ordering::SeqCst);

    if output.status.success() {
        app.emit("log", LogEvent {
            message: "SHUTDOWN COMPLETE - ENTERING STANDBY".to_string(),
            level: "info".to_string(),
            timestamp: get_timestamp(),
        }).ok();
    } else {
        let error = String::from_utf8_lossy(&output.stderr);
        app.emit("log", LogEvent {
            message: format!("SHUTDOWN ERROR: {}", error),
            level: "error".to_string(),
            timestamp: get_timestamp(),
        }).ok();
    }

    app.emit("status", StatusEvent { running: false, starting: false }).ok();
    Ok(())
}

#[tauri::command]
fn get_running() -> bool {
    IS_RUNNING.load(Ordering::SeqCst)
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            check_docker,
            check_status,
            start_services,
            stop_services,
            get_running,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
