from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import asyncio
from app import db
from app.models import User

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile', methods=['GET', 'POST'])
@login_required
async def profile():
    if request.method == 'POST':
        try:
            data = request.json
            current_user.address = data.get('address')
            current_user.company = data.get('company')
            current_user.interested_companies = data.get('interested_companies')
            
            await asyncio.to_thread(db.session.commit)
            return jsonify({'status': 'success', 'message': 'Profile updated successfully'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    return render_template('profile.html', user=current_user)

@main.route('/user/preferences', methods=['GET', 'PUT'])
@login_required
async def user_preferences():
    if request.method == 'PUT':
        try:
            data = request.json
            current_user.interested_companies = data.get('interested_companies')
            await asyncio.to_thread(db.session.commit)
            return jsonify({'status': 'success', 'message': 'Preferences updated successfully'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
    
    return jsonify({
        'interested_companies': current_user.interested_companies
    })
