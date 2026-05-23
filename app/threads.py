from flask import Blueprint, request, jsonify
import requests
import threading
import time

threads_bp = Blueprint('threads', __name__)

def make_request(url: str, results: list, index: int):
    """Single GET request karo aur result store karo"""
    try:
        response = requests.get(url, timeout=60)
        results[index] = {
            'status_code': response.status_code,
            'success': True
        }
        print(f"Request {index + 1} completed - Status: {response.status_code}")
    except Exception as e:
        results[index] = {
            'success': False,
            'error': str(e)
        }
        print(f"Request {index + 1} failed - Error: {str(e)}")

@threads_bp.route('/process', methods=['GET'])
def concurrent_requests():
    delay_value = request.args.get('delay_value')

    if not delay_value:
        return jsonify({'error': 'delay_value is required'}), 400

    try:
        delay_value = int(delay_value)
    except ValueError:
        return jsonify({'error': 'delay_value must be an integer'}), 400

    if delay_value < 0:
        return jsonify({'error': 'delay_value must be positive'}), 400


    url = f'https://httpbin.org/delay/{delay_value}'

    results = [None] * 5
    threads = []

    print(f"Starting 5 concurrent requests to {url}")

    start_time = time.time()


    for i in range(5):
        thread = threading.Thread(
            target=make_request,
            args=(url, results, i)
        )
        threads.append(thread)
        thread.start()


    for thread in threads:
        thread.join()

    end_time = time.time()
    time_taken = round(end_time - start_time, 2)

    print(f"All requests completed in {time_taken} seconds")

    return jsonify({'time_taken': time_taken}), 200