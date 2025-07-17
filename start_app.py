import subprocess
import sys
import os
import time
import webbrowser
import signal
import atexit

def run_backend():
    """Start the Flask backend API"""
    print("Starting Flask backend API...")
    backend_process = subprocess.Popen(
        [sys.executable, "api.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    return backend_process

def run_frontend():
    """Start the Electron frontend"""
    print("Starting Electron frontend...")
    electron_app_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "electron-app", "electron-app")
    
    # First, make sure all dependencies are installed
    print("Installing dependencies...")
    subprocess.run(
        ["npm", "install"],
        cwd=electron_app_path,
        shell=True,
        check=True
    )
    
    # Start the frontend
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=electron_app_path,
        shell=True
    )
    return frontend_process

def cleanup_processes(processes):
    """Cleanup processes on exit"""
    for process in processes:
        if process:
            print(f"Terminating process with PID {process.pid}...")
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()

if __name__ == "__main__":
    processes = []
    
    try:
        # Start the backend
        backend_process = run_backend()
        processes.append(backend_process)
        
        # Wait for backend to start
        print("Waiting for backend to start...")
        time.sleep(2)
        
        # Start the frontend
        frontend_process = run_frontend()
        processes.append(frontend_process)
        
        # Register cleanup function
        atexit.register(cleanup_processes, processes)
        
        print("\nInterview Mocker is running!")
        print("Backend API: http://127.0.0.1:5000")
        print("Press Ctrl+C to stop all services\n")
        
        # Keep the script running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down Interview Mocker...")
    finally:
        cleanup_processes(processes)
