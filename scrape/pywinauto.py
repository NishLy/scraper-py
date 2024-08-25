import time
from pywinauto.application import Application

def wait_for_element(window, control_title, control_type, timeout=30):
    """
    Wait for a UI element to appear within a timeout period.

    :param window: The window object to search within.
    :param control_title: The title of the UI element.
    :param control_type: The control type of the UI element (e.g., 'Button').
    :param timeout: Time to wait for the element to appear.
    :return: The control object if found, None otherwise.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            control = window.child_window(title=control_title, control_type=control_type)
            if control.exists(timeout=1):
                return control
        except TimeoutError:
            pass
        time.sleep(1)
    return None

def run_app(app_path:str,**kwargs):
    return Application(**kwargs).start(app_path)

def connect_to_app(process=None,path=None,timeout=30,backend='uia'):
    return Application(backend=backend).connect(process=process, timeout=timeout,path=path)


def wait_for_window(app, title_regex, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            window = app.window(title_re=title_regex)
            window.wait("visible", timeout=1)
            window.wait("ready", timeout=1)
            return window
        except Exception:
            time.sleep(1)
    return None

def attach_to_existing_window(title_regex, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Create a new Application object to connect to the window
            app = Application(backend="uia").connect(title_re=title_regex)
            return app
        except Exception as e:
            print(f"Error while attaching to window: {e}")
    return None