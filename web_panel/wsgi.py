#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI Entry Point for Production Deployment
"""

from app import app, db

# Database'i initialize et
with app.app_context():
    db.create_all()
    
    # Admin kullanıcısı yoksa oluştur
    from app import User
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', email='admin@example.com', subscription_type='enterprise')
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()

if __name__ == "__main__":
    app.run()
