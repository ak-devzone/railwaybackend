from celery import shared_task
from firebase_admin import firestore
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_daily_admin_report():
    """
    Send daily admin report at 9 AM
    Fetches statistics from Firestore and sends email
    """
    try:
        db = firestore.client()
        
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Fetch all users
        users_ref = db.collection('users')
        users = list(users_ref.stream())
        total_users = len(users)
        active_users = len([u for u in users if u.to_dict().get('isActive', False)])
        
        # Fetch today's sessions
        sessions_ref = db.collection('sessions')
        sessions_query = sessions_ref.where('date', '==', today)
        sessions = list(sessions_query.stream())
        total_sessions = len(sessions)
        
        # Calculate average duration
        if total_sessions > 0:
            total_duration = sum([s.to_dict().get('duration', 0) for s in sessions])
            avg_duration = int(total_duration / total_sessions / 60)  # Convert to minutes
        else:
            avg_duration = 0
        
        # Create email content
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .stat-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    margin: 15px 0;
                    border-left: 4px solid #667eea;
                    border-radius: 5px;
                }}
                .stat-number {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #667eea;
                    margin: 10px 0;
                }}
                .stat-label {{
                    font-size: 14px;
                    color: #666;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #999;
                    font-size: 12px;
                    border-top: 1px solid #eee;
                    margin-top: 30px;
                }}
                .container {{
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Digital Library System</h1>
                    <p>Daily Analytics Report - {today}</p>
                </div>
                
                <div style="padding: 30px;">
                    <h2>Today's Statistics</h2>
                    
                    <div class="stat-card">
                        <div class="stat-label">Total Users</div>
                        <div class="stat-number">{total_users}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-label">Active Users</div>
                        <div class="stat-number">{active_users}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-label">Sessions Today</div>
                        <div class="stat-number">{total_sessions}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-label">Average Session Duration</div>
                        <div class="stat-number">{avg_duration} min</div>
                    </div>
                    
                    <p style="margin-top: 30px; padding: 15px; background: #e3f2fd; border-radius: 5px;">
                        <strong>💡 Tip:</strong> Login to the admin dashboard for detailed analytics, 
                        user activity heatmap, and session timeline.
                    </p>
                </div>
                
                <div class="footer">
                    <p>This is an automated daily report from Digital Library System</p>
                    <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_message = f"""
        Digital Library System - Daily Analytics Report
        Date: {today}
        
        Today's Statistics:
        
        Total Users: {total_users}
        Active Users: {active_users}
        Sessions Today: {total_sessions}
        Average Session Duration: {avg_duration} minutes
        
        Login to the admin dashboard for detailed analytics.
        """
        
        # Send email
        send_mail(
            subject=f'📊 Daily Report - {today}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Daily report sent successfully for {today}")
        return f"Daily report sent: {total_sessions} sessions today"
        
    except Exception as e:
        logger.error(f"Error sending daily report: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def send_weekly_admin_report():
    """
    Send weekly admin report every Monday at 9 AM
    Fetches statistics for the past 7 days
    """
    try:
        db = firestore.client()
        
        # Get date range for the past week
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        today_str = today.strftime('%Y-%m-%d')
        week_ago_str = week_ago.strftime('%Y-%m-%d')
        
        # Fetch all users
        users_ref = db.collection('users')
        users = list(users_ref.stream())
        total_users = len(users)
        active_users = len([u for u in users if u.to_dict().get('isActive', False)])
        
        # Fetch this week's sessions
        sessions_ref = db.collection('sessions')
        sessions_query = sessions_ref.where('date', '>=', week_ago_str).where('date', '<=', today_str)
        sessions = list(sessions_query.stream())
        total_sessions = len(sessions)
        
        # Calculate average duration
        if total_sessions > 0:
            total_duration = sum([s.to_dict().get('duration', 0) for s in sessions])
            avg_duration = int(total_duration / total_sessions / 60)
        else:
            avg_duration = 0
        
        # Create email content
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .stat-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    margin: 15px 0;
                    border-left: 4px solid #667eea;
                    border-radius: 5px;
                }}
                .stat-number {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #667eea;
                    margin: 10px 0;
                }}
                .stat-label {{
                    font-size: 14px;
                    color: #666;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #999;
                    font-size: 12px;
                    border-top: 1px solid #eee;
                    margin-top: 30px;
                }}
                .container {{
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Digital Library System</h1>
                    <p>Weekly Analytics Report</p>
                    <p style="font-size: 14px; opacity: 0.9;">{week_ago_str} to {today_str}</p>
                </div>
                
                <div style="padding: 30px;">
                    <h2>This Week's Statistics</h2>
                    
                    <div class="stat-card">
                        <div class="stat-label">Total Users</div>
                        <div class="stat-number">{total_users}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-label">Active Users</div>
                        <div class="stat-number">{active_users}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-label">Sessions This Week</div>
                        <div class="stat-number">{total_sessions}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-label">Average Session Duration</div>
                        <div class="stat-number">{avg_duration} min</div>
                    </div>
                    
                    <p style="margin-top: 30px; padding: 15px; background: #e3f2fd; border-radius: 5px;">
                        <strong>💡 Tip:</strong> Login to the admin dashboard for detailed analytics, 
                        user activity heatmap, and session timeline.
                    </p>
                </div>
                
                <div class="footer">
                    <p>This is an automated weekly report from Digital Library System</p>
                    <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_message = f"""
        Digital Library System - Weekly Analytics Report
        Period: {week_ago_str} to {today_str}
        
        This Week's Statistics:
        
        Total Users: {total_users}
        Active Users: {active_users}
        Sessions This Week: {total_sessions}
        Average Session Duration: {avg_duration} minutes
        
        Login to the admin dashboard for detailed analytics.
        """
        
        # Send email
        send_mail(
            subject=f'📊 Weekly Report - {week_ago_str} to {today_str}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Weekly report sent successfully for {week_ago_str} to {today_str}")
        return f"Weekly report sent: {total_sessions} sessions this week"
        
    except Exception as e:
        logger.error(f"Error sending weekly report: {str(e)}")
        return f"Error: {str(e)}"
