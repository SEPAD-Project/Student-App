import win32gui
import time
import requests
import os 
import configparser

config_path = os.path.join(os.path.dirname(__file__), '../config.ini')
config = configparser.ConfigParser()
config.read(config_path)

ip_address = config['Server']['IP']
port = config['Server']['Open_window_port']

EXCLUDED_CLASSES = {
    'CEF-1004', 'Windows.UI.Core.CoreWindow',
    'Progman', 'WorkerW', 'HwndWrapper'
}

def get_user_windows():
    """Get list of user windows with error handling"""
    try:
        windows = []
        def enum_callback(hwnd, _):
            try:
                if (win32gui.IsWindowVisible(hwnd) and 
                    win32gui.GetWindowText(hwnd) and 
                    win32gui.GetClassName(hwnd) not in EXCLUDED_CLASSES and
                    win32gui.GetParent(hwnd) == 0):
                    
                    windows.append(win32gui.GetWindowText(hwnd))
            except Exception as e:
                print(f"Window enumeration error: {str(e)}")
            return True
        
        win32gui.EnumWindows(enum_callback, None)
        return windows
    
    except Exception as e:
        print(f"Failed to get windows: {str(e)}")
        return []

def send_data(school, class_name, student_id):
    """Send window data to server with comprehensive error handling"""
    try:
        # Get active window
        try:
            active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        except Exception as e:
            print(f"Failed to get active window: {str(e)}")
            active_window = "Unknown"

        # Prepare payload
        payload = {
            'school': school,
            'class': class_name,
            'student_id': student_id,
            'windows': {
                'active': active_window,
                'open_windows': get_user_windows(),
                'timestamp': time.time()
            }
        }

        # Send request
        response = requests.post(
            f"http://{ip_address}:{port}/save",
            json=payload,
            timeout=5
        )
        
        if not response.ok:
            print(f"Server responded with error: {response.status_code} - {response.text}")
            
        return response.ok
    
    except requests.exceptions.RequestException as e:
        print(f"Network error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    
    return False

def main_loop(school, class_name, student_id, interval=5):
    """Continuous sending loop with keyboard interrupt handling"""
    try:
        print(f"Sending result started... (Press Ctrl+C to stop)")
        while True:
            send_data(school, class_name, student_id)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nSending result stopped by user")

if __name__ == "__main__":
    # Configuration
    SCHOOL_NAME = "123"
    CLASS_NAME = "1052"
    STUDENT_ID = "09295"
    
    # Run continuous loop
    # main_loop(SCHOOL_NAME, CLASS_NAME, STUDENT_ID)
    
    # For single execution (without loop):
    send_data(SCHOOL_NAME, CLASS_NAME, STUDENT_ID)