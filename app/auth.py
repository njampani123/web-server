from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import asyncio
from app.models import User
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
async def register():
    if request.method == 'POST':
        try:
            data = request.json
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'status': 'error', 'message': 'Username already exists'}), 400

            user = User(
                username=data['username'],
                password=generate_password_hash(data['password'])
            )
            db.session.add(user)
            await asyncio.to_thread(db.session.commit)
            return jsonify({'status': 'success', 'message': 'Registration successful'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
async def login():
    if request.method == 'POST':
        try:
            data = request.json
            user = await asyncio.to_thread(
                lambda: User.query.filter_by(username=data['username']).first()
            )
            
            if user and check_password_hash(user.password, data['password']):
                login_user(user)
                return jsonify({'status': 'success', 'message': 'Login successful'})
            
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
