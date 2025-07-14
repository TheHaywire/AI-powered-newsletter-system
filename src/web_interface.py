"""
AI Newsletter Web Interface
Flask-based web interface for managing the newsletter system
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from typing import Dict, Any, List
import plotly.graph_objs as go
import plotly.utils
import pandas as pd

# Import our newsletter components
from newsletter_orchestrator import NewsletterOrchestrator
from email_distributor import EmailDistributor

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize newsletter components
orchestrator = NewsletterOrchestrator()
email_distributor = EmailDistributor()

class User(UserMixin):
    """Simple user model for authentication"""
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

# Simple user database (in production, use a proper database)
users = {
    'admin': User(1, 'admin', 'admin123')
}

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

@app.route('/')
@login_required
def dashboard():
    """Main dashboard"""
    # Get system statistics
    stats = get_system_stats()
    
    # Get recent newsletters
    recent_newsletters = get_recent_newsletters()
    
    # Get subscriber stats
    subscriber_stats = email_distributor.get_subscriber_stats()
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_newsletters=recent_newsletters,
                         subscriber_stats=subscriber_stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username].password == password:
            login_user(users[username])
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate_newsletter():
    """Generate a new newsletter"""
    if request.method == 'POST':
        theme = request.form.get('theme', 'Technology & Innovation')
        
        try:
            # Generate newsletter
            report = orchestrator.generate_newsletter(theme)
            
            flash(f'Newsletter generated successfully: {report["newsletter"].title}')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f'Error generating newsletter: {str(e)}')
    
    return render_template('generate.html')

@app.route('/newsletters')
@login_required
def newsletters():
    """View all newsletters"""
    newsletters = get_all_newsletters()
    return render_template('newsletters.html', newsletters=newsletters)

@app.route('/newsletter/<newsletter_id>')
@login_required
def view_newsletter(newsletter_id):
    """View a specific newsletter"""
    newsletter = get_newsletter_by_id(newsletter_id)
    if newsletter:
        return render_template('view_newsletter.html', newsletter=newsletter)
    else:
        flash('Newsletter not found')
        return redirect(url_for('newsletters'))

@app.route('/subscribers')
@login_required
def subscribers():
    """Manage subscribers"""
    subscribers = email_distributor.get_active_subscribers()
    return render_template('subscribers.html', subscribers=subscribers)

@app.route('/subscribers/add', methods=['POST'])
@login_required
def add_subscriber():
    """Add a new subscriber"""
    email = request.form.get('email')
    name = request.form.get('name', '')
    
    if email:
        success = email_distributor.add_subscriber(email, name)
        if success:
            flash(f'Subscriber added: {email}')
        else:
            flash(f'Failed to add subscriber: {email}')
    
    return redirect(url_for('subscribers'))

@app.route('/subscribers/remove/<email>')
@login_required
def remove_subscriber(email):
    """Remove a subscriber"""
    success = email_distributor.remove_subscriber(email)
    if success:
        flash(f'Subscriber removed: {email}')
    else:
        flash(f'Failed to remove subscriber: {email}')
    
    return redirect(url_for('subscribers'))

@app.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard"""
    # Get analytics data
    analytics_data = get_analytics_data()
    
    # Create charts
    charts = create_analytics_charts(analytics_data)
    
    return render_template('analytics.html', charts=charts, data=analytics_data)

@app.route('/settings')
@login_required
def settings():
    """System settings"""
    config = load_config()
    return render_template('settings.html', config=config)

@app.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    """Update system settings"""
    # Update configuration based on form data
    config = load_config()
    
    # Update config with form data
    config['newsletter_theme'] = request.form.get('theme', config['newsletter_theme'])
    config['quality_thresholds']['min_articles'] = int(request.form.get('min_articles', 5))
    
    # Save config
    save_config(config)
    
    flash('Settings updated successfully')
    return redirect(url_for('settings'))

@app.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for statistics"""
    stats = get_system_stats()
    return jsonify(stats)

@app.route('/api/generate', methods=['POST'])
@login_required
def api_generate():
    """API endpoint for newsletter generation"""
    data = request.get_json()
    theme = data.get('theme', 'Technology & Innovation')
    
    try:
        report = orchestrator.generate_newsletter(theme)
        return jsonify({
            'success': True,
            'newsletter': {
                'title': report['newsletter'].title,
                'word_count': report['newsletter'].word_count,
                'reading_time': report['newsletter'].reading_time
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

def get_system_stats() -> Dict[str, Any]:
    """Get system statistics"""
    # Count files in output directory
    output_dir = Path("output")
    if output_dir.exists():
        newsletter_files = list(output_dir.glob("newsletter_*.md"))
        total_newsletters = len(newsletter_files)
    else:
        total_newsletters = 0
    
    # Get subscriber stats
    subscriber_stats = email_distributor.get_subscriber_stats()
    
    # Get recent activity
    recent_activity = get_recent_activity()
    
    return {
        'total_newsletters': total_newsletters,
        'subscribers': subscriber_stats['active_subscribers'],
        'recent_activity': recent_activity,
        'system_status': 'healthy'
    }

def get_recent_newsletters() -> List[Dict[str, Any]]:
    """Get recent newsletters"""
    output_dir = Path("output")
    newsletters = []
    
    if output_dir.exists():
        for file_path in sorted(output_dir.glob("newsletter_*.md"), reverse=True)[:10]:
            # Extract date from filename
            filename = file_path.stem
            if '_' in filename:
                date_str = filename.split('_')[-1]
                try:
                    date = datetime.strptime(date_str, "%Y%m%d")
                    newsletters.append({
                        'id': filename,
                        'title': f"Newsletter - {date.strftime('%B %d, %Y')}",
                        'date': date,
                        'file_path': str(file_path)
                    })
                except ValueError:
                    continue
    
    return newsletters

def get_all_newsletters() -> List[Dict[str, Any]]:
    """Get all newsletters"""
    return get_recent_newsletters()

def get_newsletter_by_id(newsletter_id: str) -> Dict[str, Any]:
    """Get newsletter by ID"""
    output_dir = Path("output")
    file_path = output_dir / f"{newsletter_id}.md"
    
    if file_path.exists():
        with open(file_path, 'r') as f:
            content = f.read()
        
        return {
            'id': newsletter_id,
            'content': content,
            'file_path': str(file_path)
        }
    
    return None

def get_recent_activity() -> List[Dict[str, Any]]:
    """Get recent system activity"""
    # This would typically come from a log file or database
    return [
        {
            'action': 'Newsletter generated',
            'timestamp': datetime.now() - timedelta(hours=2),
            'details': 'Technology & Innovation Weekly'
        },
        {
            'action': 'Subscriber added',
            'timestamp': datetime.now() - timedelta(hours=4),
            'details': 'john@example.com'
        }
    ]

def get_analytics_data() -> Dict[str, Any]:
    """Get analytics data"""
    # This would typically come from a database
    return {
        'newsletter_generation': {
            'daily': [5, 3, 7, 4, 6, 8, 5],
            'weekly': [25, 30, 28, 35, 32, 38, 40]
        },
        'subscriber_growth': {
            'daily': [2, 1, 3, 2, 4, 1, 3],
            'weekly': [10, 12, 15, 18, 20, 22, 25]
        },
        'email_metrics': {
            'open_rate': 0.68,
            'click_rate': 0.12,
            'bounce_rate': 0.02
        }
    }

def create_analytics_charts(data: Dict[str, Any]) -> Dict[str, str]:
    """Create analytics charts using Plotly"""
    charts = {}
    
    # Newsletter generation chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        y=data['newsletter_generation']['daily'],
        mode='lines+markers',
        name='Daily Generation'
    ))
    fig.update_layout(title='Newsletter Generation (Daily)', xaxis_title='Day', yaxis_title='Count')
    charts['newsletter_generation'] = plotly.utils.PlotlyJSONEncoder().encode(fig)
    
    # Subscriber growth chart
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7'],
        y=data['subscriber_growth']['weekly'],
        name='Subscriber Growth'
    ))
    fig2.update_layout(title='Subscriber Growth (Weekly)', xaxis_title='Week', yaxis_title='New Subscribers')
    charts['subscriber_growth'] = plotly.utils.PlotlyJSONEncoder().encode(fig2)
    
    return charts

def load_config() -> Dict[str, Any]:
    """Load system configuration"""
    config_path = "config/orchestrator_config.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_config(config: Dict[str, Any]):
    """Save system configuration"""
    config_path = "config/orchestrator_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    Path("templates").mkdir(exist_ok=True)
    
    # Create basic templates
    create_basic_templates()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

def create_basic_templates():
    """Create basic HTML templates"""
    templates_dir = Path("templates")
    
    # Base template
    base_template = """<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}AI Newsletter Generator{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">AI Newsletter Generator</a>
            {% if current_user.is_authenticated %}
            <div class="navbar-nav">
                <a class="nav-link" href="{{ url_for('dashboard') }}">Dashboard</a>
                <a class="nav-link" href="{{ url_for('generate_newsletter') }}">Generate</a>
                <a class="nav-link" href="{{ url_for('newsletters') }}">Newsletters</a>
                <a class="nav-link" href="{{ url_for('subscribers') }}">Subscribers</a>
                <a class="nav-link" href="{{ url_for('analytics') }}">Analytics</a>
                <a class="nav-link" href="{{ url_for('settings') }}">Settings</a>
                <a class="nav-link" href="{{ url_for('logout') }}">Logout</a>
            </div>
            {% endif %}
        </div>
    </nav>
    
    <div class="container mt-4">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-info">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    with open(templates_dir / "base.html", "w") as f:
        f.write(base_template)
    
    # Dashboard template
    dashboard_template = """{% extends "base.html" %}
{% block title %}Dashboard - AI Newsletter Generator{% endblock %}

{% block content %}
<h1>Dashboard</h1>

<div class="row">
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Total Newsletters</h5>
                <h2>{{ stats.total_newsletters }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Active Subscribers</h5>
                <h2>{{ subscriber_stats.active_subscribers }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">System Status</h5>
                <h2 class="text-success">{{ stats.system_status }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Recent Activity</h5>
                <h2>{{ stats.recent_activity|length }}</h2>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h5>Recent Newsletters</h5>
            </div>
            <div class="card-body">
                {% if recent_newsletters %}
                <div class="list-group">
                    {% for newsletter in recent_newsletters %}
                    <a href="{{ url_for('view_newsletter', newsletter_id=newsletter.id) }}" class="list-group-item list-group-item-action">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">{{ newsletter.title }}</h6>
                            <small>{{ newsletter.date.strftime('%B %d, %Y') }}</small>
                        </div>
                    </a>
                    {% endfor %}
                </div>
                {% else %}
                <p class="text-muted">No newsletters generated yet.</p>
                {% endif %}
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5>Quick Actions</h5>
            </div>
            <div class="card-body">
                <a href="{{ url_for('generate_newsletter') }}" class="btn btn-primary btn-block w-100 mb-2">Generate Newsletter</a>
                <a href="{{ url_for('subscribers') }}" class="btn btn-secondary btn-block w-100 mb-2">Manage Subscribers</a>
                <a href="{{ url_for('analytics') }}" class="btn btn-info btn-block w-100">View Analytics</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    
    with open(templates_dir / "dashboard.html", "w") as f:
        f.write(dashboard_template)
    
    # Login template
    login_template = """{% extends "base.html" %}
{% block title %}Login - AI Newsletter Generator{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3>Login</h3>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Login</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    
    with open(templates_dir / "login.html", "w") as f:
        f.write(login_template) 