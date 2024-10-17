from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute_file():
    # Extracting the parameters from the JSON body of the request
    data = request.json
    ip = data.get('ip')
    port = data.get('port')
    time = data.get('time')
    thread = data.get('thread')

    # Check if all required parameters are provided
    if not all([ip, port, time, thread]):
        return jsonify({'status': 'error', 'message': 'Missing required parameters'}), 400

    # Construct the command to execute
    command = f"./file {ip} {port} {time} {thread}"

    try:
        # Execute the command and capture the output
        output = subprocess.check_output(command, shell=True)
        return jsonify({'status': 'success', 'output': output.decode('utf-8')})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
