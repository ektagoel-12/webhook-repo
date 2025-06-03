from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import hashlib
import hmac
import os
from bson import ObjectId
import json

app = Flask(__name__)

try:
    client = MongoClient('mongodb+srv://ektagoel12:helloworld12@cluster0.el4h76v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
    db = client['github_webhooks']
    collection = db['events']
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    client = None
    db = None
    collection = None

WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'your_webhook_secret_key')

def verify_signature(payload_body, signature_header):
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)

def format_timestamp(timestamp_str):
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%d %B %Y - %I:%M %p UTC").replace(' 0', ' ')
    except:
        return timestamp_str

def get_ordinal_suffix(day):
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return str(day) + suffix

def format_timestamp_custom(timestamp_str):
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        day_with_suffix = get_ordinal_suffix(dt.day)
        month = dt.strftime("%B")
        year = dt.year
        time = dt.strftime("%I:%M %p")
        return f"{day_with_suffix} {month} {year} - {time} UTC"
    except:
        return timestamp_str

@app.route('/webhook', methods=['POST'])
def github_webhook():
    try:
        signature = request.headers.get('X-Hub-Signature-256')
        if WEBHOOK_SECRET != 'your_webhook_secret_key':  # Only verify if secret is set
            if not verify_signature(request.data, signature):
                return jsonify({'error': 'Invalid signature'}), 401

        event_type = request.headers.get('X-GitHub-Event')
        payload = request.json

        if not payload:
            return jsonify({'error': 'No payload received'}), 400

        event_data = None

        if event_type == 'push':
            author = payload['pusher']['name']
            to_branch = payload['ref'].split('/')[-1]  # Extract branch name from refs/heads/branch_name
            timestamp = payload['head_commit']['timestamp']
            
            event_data = {
                'request_id': str(ObjectId()),
                'author': author,
                'action': 'PUSH',
                'from_branch': None,
                'to_branch': to_branch,
                'timestamp': timestamp,
                'formatted_message': f'"{author}" pushed to "{to_branch}" on {format_timestamp_custom(timestamp)}'
            }

        elif event_type == 'pull_request':
            if payload['action'] in ['opened', 'reopened']:
                author = payload['pull_request']['user']['login']
                from_branch = payload['pull_request']['head']['ref']
                to_branch = payload['pull_request']['base']['ref']
                timestamp = payload['pull_request']['created_at']
                
                event_data = {
                    'request_id': str(ObjectId()),
                    'author': author,
                    'action': 'PULL_REQUEST',
                    'from_branch': from_branch,
                    'to_branch': to_branch,
                    'timestamp': timestamp,
                    'formatted_message': f'"{author}" submitted a pull request from "{from_branch}" to "{to_branch}" on {format_timestamp_custom(timestamp)}'
                }
            
            elif payload['action'] == 'closed' and payload['pull_request']['merged']:
                author = payload['pull_request']['merged_by']['login'] if payload['pull_request']['merged_by'] else payload['pull_request']['user']['login']
                from_branch = payload['pull_request']['head']['ref']
                to_branch = payload['pull_request']['base']['ref']
                timestamp = payload['pull_request']['merged_at']
                
                event_data = {
                    'request_id': str(ObjectId()),
                    'author': author,
                    'action': 'MERGE',
                    'from_branch': from_branch,
                    'to_branch': to_branch,
                    'timestamp': timestamp,
                    'formatted_message': f'"{author}" merged branch "{from_branch}" to "{to_branch}" on {format_timestamp_custom(timestamp)}'
                }

        if event_data and collection is not None:
            try:
                result = collection.insert_one(event_data)
                print(f"Stored event: {event_data['formatted_message']}")
                return jsonify({'status': 'success', 'id': str(result.inserted_id)}), 200
            except Exception as e:
                print(f"Failed to store in MongoDB: {e}")
                return jsonify({'error': 'Database error'}), 500
        
        elif event_data:
            print(f"Event received: {event_data['formatted_message']}")
            return jsonify({'status': 'success', 'message': 'Event processed (no database)'}), 200

        return jsonify({'status': 'ignored', 'event_type': event_type}), 200

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/events')
def get_events():
    try:
        if collection is None:
            sample_events = [
                {
                    'formatted_message': '"John" pushed to "main" on 1st June 2025 - 10:30 AM UTC',
                    'timestamp': datetime.now().isoformat(),
                    'action': 'PUSH'
                }
            ]
            return jsonify(sample_events)

        events = list(collection.find().sort('timestamp', -1).limit(20))
        
        # Convert ObjectId to string for JSON serialization
        for event in events:
            if '_id' in event:
                event['_id'] = str(event['_id'])
        
        return jsonify(events)
    
    except Exception as e:
        print(f"Error fetching events: {e}")
        return jsonify([])

@app.route('/test')
def test_endpoint():
    return jsonify({
        'status': 'running',
        'message': 'Webhook endpoint is ready!',
        'mongodb_connected': collection is not None
    })

if __name__ == '__main__':
    print("Starting GitHub Webhook Receiver...")
    print("Dashboard available at: http://localhost:5000")
    print("Webhook endpoint: http://localhost:5000/webhook")
    
    app.run(debug=True, host='0.0.0.0', port=5000)