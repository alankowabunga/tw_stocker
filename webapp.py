from flask import Flask, render_template, send_from_directory, jsonify, request
import subprocess
import os
import threading
import time

app = Flask(__name__, template_folder='templates')

# Path settings
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_FILE = os.path.join(ROOT_DIR, 'stock_report.html')
LOG_FILE = os.path.join(ROOT_DIR, 'run.log')
RUN_SCRIPT = os.path.join(ROOT_DIR, 'run.sh')

# Process handle
process = None
process_lock = threading.Lock()


def is_running():
    with process_lock:
        return process is not None and process.poll() is None


def start_run_sh():
    """Start run.sh in background and redirect output to run.log. Returns True if started, False if already running."""
    global process
    with process_lock:
        if process is not None and process.poll() is None:
            return False
        # ensure script is executable
        os.chmod(RUN_SCRIPT, 0o755)
        f = open(LOG_FILE, 'ab')
        process = subprocess.Popen([RUN_SCRIPT], stdout=f, stderr=subprocess.STDOUT, cwd=ROOT_DIR)
        return True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/report')
def report():
    if os.path.exists(REPORT_FILE):
        return send_from_directory(ROOT_DIR, 'stock_report.html')
    return "Report not found. Run recommend first.", 404


@app.route('/portfolio')
def portfolio():
    portfolio_file = os.path.join(ROOT_DIR, 'portfolio_plot.html')
    if os.path.exists(portfolio_file):
        return send_from_directory(ROOT_DIR, 'portfolio_plot.html')
    return "Portfolio plot not found. Run example first.", 404


@app.route('/run', methods=['POST'])
def run_once():
    started = start_run_sh()
    if started:
        return jsonify({"status": "started"}), 202
    else:
        return jsonify({"status": "already_running"}), 409


@app.route('/status')
def status():
    running = is_running()
    # tail last 5000 chars from log
    log_tail = ''
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'rb') as f:
                f.seek(0, os.SEEK_END)
                size = f.tell()
                to_read = min(size, 20000)
                f.seek(size - to_read)
                log_tail = f.read().decode(errors='ignore')
        except Exception:
            log_tail = 'Unable to read log.'
    return jsonify({"running": running, "log": log_tail})


if __name__ == '__main__':
    # Run on 0.0.0.0:5000 by default
    app.run(host='0.0.0.0', port=5000, debug=False)
