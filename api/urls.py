from django.urls import path, include
from .views import health_check, send_admin_welcome
from .views_email import send_welcome_email, send_password_reset_email
from .views_upload import upload_id_proof
from .views_reports import send_admin_report
from .views_books import (
    upload_book, 
    list_books, 
    get_book_details, 
    update_book, 
    delete_book, 
    check_book_access
)
from .views_payments import (
    initiate_payment,
    verify_payment,
    get_user_purchases,
    get_my_library
)
from .views_analytics import (
    get_dashboard_analytics,
    get_revenue_analytics,
    get_user_analytics,
    track_book_view,
    track_book_download
)
from .views_users import (
    list_users,
    get_user_details,
    verify_id_proof,
    suspend_user,
    update_user,
    get_user_analytics as get_user_mgmt_analytics,
    get_user_session_history,
    complete_profile,
    register_user,
    register_user,
    sync_user
)
from .views_admin import register_admin, get_admin_details
from .views_files import serve_database_file

urlpatterns = [
    # Health check
    path('health/', health_check, name='health'),
    path('send-welcome-email/', send_welcome_email, name='send-welcome-email'),
    path('send-password-reset-email/', send_password_reset_email, name='send-password-reset-email'),
    path('upload-id-proof/', upload_id_proof, name='upload-id-proof'),
    path('send-admin-report/', send_admin_report, name='send-admin-report'),
    path('send-admin-welcome/', send_admin_welcome, name='send-admin-welcome'),
    
    # User Routes
    path('users/register/', register_user, name='register-user'),
    path('users/sync/', sync_user, name='sync-user'),
    path('users/profile/complete/', complete_profile, name='complete-profile'),
    
    # Admin Routes
    path('admin/register/', register_admin, name='register-admin'),
    path('admin/profile/<str:admin_id>/', get_admin_details, name='get-admin-profile'),
    
    # Book Management
    path('books/upload/', upload_book, name='upload-book'),
    path('books/', list_books, name='list-books'),
    path('books/<str:book_id>/', get_book_details, name='get-book-details'),
    path('books/<str:book_id>/update/', update_book, name='update-book'),
    path('books/<str:book_id>/delete/', delete_book, name='delete-book'),
    path('books/<str:book_id>/access/', check_book_access, name='check-book-access'),
    path('books/<str:book_id>/track-view/', track_book_view, name='track-book-view'),
    path('books/<str:book_id>/track-download/', track_book_download, name='track-book-download'),
    
    # Payment & Purchases
    path('books/<str:book_id>/purchase/', initiate_payment, name='initiate-payment'),
    path('books/<str:book_id>/verify-payment/', verify_payment, name='verify-payment'),
    path('purchases/', get_user_purchases, name='get-user-purchases'),
    path('my-library/', get_my_library, name='get-my-library'),
    
    # Analytics
    path('analytics/dashboard/', get_dashboard_analytics, name='dashboard-analytics'),
    path('analytics/revenue/', get_revenue_analytics, name='revenue-analytics'),
    path('analytics/users/', get_user_analytics, name='user-analytics'),
    
    # User Management (analytics must come before dynamic user_id route)
    path('admin/users/analytics/', get_user_mgmt_analytics, name='user-mgmt-analytics'),
    path('admin/users/', list_users, name='list-users'),
    path('admin/users/<str:user_id>/', get_user_details, name='get-user-details'),
    path('admin/users/<str:user_id>/update/', update_user, name='update-user'),
    path('admin/users/<str:user_id>/verify-id/', verify_id_proof, name='verify-id-proof'),
    path('admin/users/<str:user_id>/suspend/', suspend_user, name='suspend-user'),
    path('admin/users/<str:user_id>/history/', get_user_session_history, name='get-user-session-history'),

    # File Serving
    path('media/<path:filename>', serve_database_file, name='serve-db-file'),
]
