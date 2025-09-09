"""
Admin Routes - Admin Dashboard and Flag Management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models.database_models import db, User, Certificate, VerificationAttempt, Flag, Institution
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('admin_routes', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check admin user
        admin_user = User.query.filter_by(username=username, user_type='admin').first()

        if admin_user and check_password_hash(admin_user.password_hash, password):
            login_user(admin_user)
            session['is_admin'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_routes.dashboard'))
        else:
            flash('Invalid admin credentials.', 'error')

    return render_template('admin/admin_login.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    if not session.get('is_admin') or current_user.user_type != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_routes.admin_login'))

    # Get dashboard statistics
    stats = get_dashboard_stats()

    # Get recent verification attempts
    recent_attempts = VerificationAttempt.query.order_by(
        VerificationAttempt.timestamp.desc()
    ).limit(20).all()

    # Get recent flags
    recent_flags = Flag.query.filter_by(is_resolved=False).order_by(
        Flag.timestamp.desc()
    ).limit(10).all()

    # Get institution flag statistics
    flag_stats = db.session.query(
        Flag.institution_name,
        func.count(Flag.id).label('flag_count'),
        func.max(Flag.timestamp).label('latest_flag')
    ).filter(
        Flag.timestamp >= datetime.now() - timedelta(days=30)
    ).group_by(Flag.institution_name).all()

    return render_template('admin/admin_dashboard.html', 
                         stats=stats,
                         recent_attempts=recent_attempts,
                         recent_flags=recent_flags,
                         flag_stats=flag_stats)

@bp.route('/flags')
@login_required
def view_flags():
    """View all flags"""
    if not session.get('is_admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_routes.admin_login'))

    page = request.args.get('page', 1, type=int)
    per_page = 20

    flags = Flag.query.order_by(Flag.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('admin/flags_list.html', flags=flags)

@bp.route('/institutions')
@login_required
def view_institutions():
    """View all institutions"""
    if not session.get('is_admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_routes.admin_login'))

    institutions = Institution.query.all()

    # Get certificate counts for each institution
    institution_stats = []
    for inst in institutions:
        cert_count = Certificate.query.filter_by(institution_name=inst.name).count()
        flag_count = Flag.query.filter_by(institution_name=inst.name).count()

        institution_stats.append({
            'institution': inst,
            'certificate_count': cert_count,
            'flag_count': flag_count,
            'risk_level': 'High' if flag_count > 5 else 'Medium' if flag_count > 2 else 'Low'
        })

    return render_template('admin/institutions_list.html', institution_stats=institution_stats)

@bp.route('/verification-logs')
@login_required
def verification_logs():
    """View verification logs"""
    if not session.get('is_admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_routes.admin_login'))

    page = request.args.get('page', 1, type=int)
    per_page = 50

    logs = VerificationAttempt.query.order_by(
        VerificationAttempt.timestamp.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/verification_logs.html', logs=logs)

@bp.route('/raise-alarm/<institution_name>')
@login_required
def raise_alarm(institution_name):
    """Raise alarm for institution"""
    if not session.get('is_admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_routes.admin_login'))

    # Create high priority flag
    alarm_flag = Flag(
        flag_type='MANUAL_ALARM',
        institution_name=institution_name,
        description=f'Manual alarm raised by admin for {institution_name}',
        severity='CRITICAL',
        timestamp=datetime.utcnow()
    )

    db.session.add(alarm_flag)

    try:
        db.session.commit()
        flash(f'Alarm raised for {institution_name}', 'warning')
    except:
        db.session.rollback()
        flash('Failed to raise alarm', 'error')

    return redirect(url_for('admin_routes.dashboard'))

@bp.route('/resolve-flag/<int:flag_id>')
@login_required
def resolve_flag(flag_id):
    """Resolve a flag"""
    if not session.get('is_admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_routes.admin_login'))

    flag = Flag.query.get_or_404(flag_id)
    flag.is_resolved = True
    flag.resolved_by = current_user.username

    try:
        db.session.commit()
        flash('Flag resolved successfully', 'success')
    except:
        db.session.rollback()
        flash('Failed to resolve flag', 'error')

    return redirect(url_for('admin_routes.view_flags'))

@bp.route('/export-logs')
@login_required
def export_logs():
    """Export verification logs as CSV"""
    if not session.get('is_admin'):
        flash('Admin access required.', 'error')
        return redirect(url_for('admin_routes.admin_login'))

    from flask import Response
    import csv
    from io import StringIO

    # Get all verification attempts
    attempts = VerificationAttempt.query.order_by(VerificationAttempt.timestamp.desc()).all()

    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['Timestamp', 'File Name', 'Status', 'Institution', 'IP Address', 'Flags'])

    # Write data
    for attempt in attempts:
        flags = ', '.join(attempt.flags_detected) if attempt.flags_detected else 'None'
        writer.writerow([
            attempt.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            attempt.file_name or 'Unknown',
            attempt.verification_status,
            attempt.institution_matched or 'Unknown',
            attempt.ip_address or 'Unknown',
            flags
        ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=verification_logs_{datetime.now().strftime("%Y%m%d")}.csv'}
    )

@bp.route('/logout')
@login_required
def admin_logout():
    """Admin logout"""
    session.pop('is_admin', None)
    logout_user()
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('verification_routes.index'))

# API endpoints
@bp.route('/api/stats')
@login_required
def api_stats():
    """Get dashboard statistics via API"""
    if not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    stats = get_dashboard_stats()
    return jsonify(stats)

def get_dashboard_stats():
    """Calculate dashboard statistics"""

    # Total counts
    total_certificates = Certificate.query.count()
    total_institutions = Institution.query.count()
    total_verification_attempts = VerificationAttempt.query.count()
    total_flags = Flag.query.count()

    # Recent activity (last 24 hours)
    yesterday = datetime.now() - timedelta(days=1)
    recent_attempts = VerificationAttempt.query.filter(
        VerificationAttempt.timestamp >= yesterday
    ).count()

    recent_flags = Flag.query.filter(
        Flag.timestamp >= yesterday
    ).count()

    # Verification success rate
    verified_attempts = VerificationAttempt.query.filter_by(
        verification_status='verified'
    ).count()
    success_rate = (verified_attempts / total_verification_attempts * 100) if total_verification_attempts > 0 else 0

    # High priority flags
    high_priority_flags = Flag.query.filter(
        Flag.severity.in_(['HIGH', 'CRITICAL']),
        Flag.is_resolved == False
    ).count()

    return {
        'total_certificates': total_certificates,
        'total_institutions': total_institutions,
        'total_verification_attempts': total_verification_attempts,
        'total_flags': total_flags,
        'recent_attempts': recent_attempts,
        'recent_flags': recent_flags,
        'success_rate': round(success_rate, 1),
        'high_priority_flags': high_priority_flags
    }
