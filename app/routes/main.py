from flask import Blueprint, redirect, url_for, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Redirect to the API docs page."""
    return redirect('/docs/')

@main_bp.route('/health')
def health():
    """Health check endpoint for container healthchecks."""
    return jsonify({"status": "healthy"}), 200 