"""
Flask Backend Server for Portfolio Website
Author: Shaik Fariya
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import init_database, add_contact, get_all_contacts, increment_visitor_count, get_visitor_count, delete_contact
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask app
app = Flask(__name__, static_folder=BASE_DIR)
CORS(app)  # Enable CORS for frontend requests

# Initialize database on startup
init_database()

# ===== Static File Routes =====
@app.route('/')
def serve_index():
    """Serve the main HTML page"""
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/admin')
def serve_admin():
    """Serve the admin dashboard page"""
    return send_from_directory(BASE_DIR, 'admin.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files and gracefully fall back to the homepage."""
    target_path = os.path.join(BASE_DIR, filename)

    if os.path.isfile(target_path):
        return send_from_directory(BASE_DIR, filename)

    if not filename.startswith('api/'):
        return send_from_directory(BASE_DIR, 'index.html')

    return jsonify({'error': 'Resource not found'}), 404

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render"""
    return jsonify({'status': 'ok'}), 200

# ===== API Routes =====

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json(silent=True) or {}
        
        # Validate required fields
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        message = data.get('message', '').strip()
        
        if not name or not email or not message:
            return jsonify({'error': 'All fields are required'}), 400
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Please enter a valid email address'}), 400
        
        # Save to database
        if add_contact(name, email, message):
            return jsonify({
                'success': True,
                'message': 'Thank you for your message! I will get back to you soon.'
            }), 200
        else:
            return jsonify({'error': 'Could not save your message. Please try again.'}), 500
            
    except Exception as e:
        print(f"Error in contact submission: {e}")
        return jsonify({'error': 'An error occurred. Please try again.'}), 500

@app.route('/api/visitor', methods=['GET'])
def get_visitor():
    """Get and increment visitor count"""
    try:
        count = increment_visitor_count()
        return jsonify({'count': count}), 200
    except Exception as e:
        print(f"Error getting visitor count: {e}")
        return jsonify({'error': 'Could not get visitor count'}), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get all contact messages (admin endpoint)"""
    try:
        contacts = get_all_contacts()
        messages = []
        for contact in contacts:
            messages.append({
                'id': contact['id'],
                'name': contact['name'],
                'email': contact['email'],
                'message': contact['message'],
                'created_at': contact['created_at']
            })
        return jsonify({'messages': messages}), 200
    except Exception as e:
        print(f"Error getting messages: {e}")
        return jsonify({'error': 'Could not fetch messages'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get website statistics"""
    try:
        visitor_count = get_visitor_count()
        contacts = get_all_contacts()
        return jsonify({
            'visitors': visitor_count,
            'messages': len(contacts)
        }), 200
    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({'error': 'Could not fetch stats'}), 500

@app.route('/api/messages/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete a contact message by ID"""
    try:
        if delete_contact(message_id):
            return jsonify({'success': True, 'message': 'Message deleted'}), 200
        else:
            return jsonify({'error': 'Could not delete message'}), 500
    except Exception as e:
        print(f"Error deleting message: {e}")
        return jsonify({'error': 'An error occurred'}), 500

# ===== Error Handlers =====
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Resource not found'}), 404
    return send_from_directory(BASE_DIR, 'index.html')

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ===== Run Server =====
if __name__ == '__main__':
    print("\n" + "="*50)
    print("   Shaik Fariya's Portfolio Server")
    print("="*50)
    print("\n🚀 Server starting...")
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 10000))
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    print(f"📍 Running on port {port}")
    print(f"🔧 Debug mode: {not is_production}")
    print("📍 Press Ctrl+C to stop the server\n")
    
    app.run(debug=not is_production, host='0.0.0.0', port=port)
