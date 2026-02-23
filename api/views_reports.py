from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_admin_report(request):
    """
    Send email report to admin with analytics summary
    """
    try:
        data = request.data
        total_users = data.get('totalUsers', 0)
        active_users = data.get('activeUsers', 0)
        total_sessions = data.get('totalSessions', 0)
        avg_duration = data.get('avgDuration', 0)

        # Create HTML email content
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
                    <p>Admin Analytics Report</p>
                </div>
                
                <div style="padding: 30px;">
                    <h2>Daily Statistics Summary</h2>
                    
                    <div class="stat-card">
                        <div class="stat-label">Total Users</div>
                        <div class="stat-number">{total_users}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-label">Active Users</div>
                        <div class="stat-number">{active_users}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-label">Total Sessions</div>
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
                    <p>This is an automated report from Digital Library System</p>
                    <p>Generated automatically</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Plain text version
        plain_message = f"""
        Digital Library System - Admin Analytics Report
        
        Daily Statistics Summary:
        
        Total Users: {total_users}
        Active Users: {active_users}
        Total Sessions: {total_sessions}
        Average Session Duration: {avg_duration} minutes
        
        Login to the admin dashboard for detailed analytics.
        """

        # Send email
        send_mail(
            subject='📊 Digital Library - Admin Analytics Report',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Admin report sent successfully to {settings.ADMIN_EMAIL}")
        
        return Response({
            'status': 'success',
            'message': 'Email report sent successfully'
        })

    except Exception as e:
        logger.error(f"Error sending admin report: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)
