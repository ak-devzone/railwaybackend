from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncDate, TruncMonth
from datetime import datetime, timedelta
from .models import Book, UserProfile, Purchase, AdminProfile
import json

@require_http_methods(["GET"])
def get_dashboard_analytics(request):
    """Get comprehensive analytics for admin dashboard"""
    try:
        # 1. Book Stats
        total_books = Book.objects.count()
        free_books = Book.objects.filter(is_premium=False).count()
        premium_books = Book.objects.filter(is_premium=True).count()
        
        # Books uploaded this month
        now = datetime.now()
        books_this_month = Book.objects.filter(
            uploaded_at__month=now.month, 
            uploaded_at__year=now.year
        ).count()
        
        # 2. User Stats
        total_students = UserProfile.objects.filter(role='student').count()
        new_students_this_month = UserProfile.objects.filter(
            role='student',
            created_at__month=now.month,
            created_at__year=now.year
        ).count()
        
        # 3. Purchase/Revenue Stats
        total_purchases = Purchase.objects.count()
        total_revenue_agg = Purchase.objects.aggregate(total=Sum('amount'))
        total_revenue = float(total_revenue_agg['total'] or 0)
        
        # 4. Recent Books
        recent_books_qs = Book.objects.all().order_by('-uploaded_at')[:10]
        recent_books_data = [{
            'id': b.id,
            'title': b.title,
            'department': b.department,
            'semester': b.semester,
            'isPremium': b.is_premium,
            'price': float(b.price)
        } for b in recent_books_qs]
        
        # 5. Popular Books (by views)
        popular_books_qs = Book.objects.all().order_by('-views')[:10]
        popular_books_data = [{
            'id': b.id,
            'title': b.title,
            'views': b.views,
            'downloads': b.downloads,
            'isPremium': b.is_premium
        } for b in popular_books_qs]
        
        # 6. Recent Purchases
        recent_purchases_qs = Purchase.objects.select_related('user', 'book').all().order_by('-purchase_date')[:10]
        recent_purchases_data = [{
            'id': p.id,
            'bookTitle': p.book.title,
            'userName': p.user.name,
            'amount': float(p.amount),
            'purchasedAt': p.purchase_date.isoformat()
        } for p in recent_purchases_qs]
        
        return JsonResponse({
            'success': True,
            'stats': {
                'totalBooks': total_books,
                'freeBooks': free_books,
                'premiumBooks': premium_books,
                'totalStudents': total_students,
                'newStudentsThisMonth': new_students_this_month,
                'totalRevenue': total_revenue,
                'booksThisMonth': books_this_month,
                'totalPurchases': total_purchases
            },
            'recentBooks': recent_books_data,
            'popularBooks': popular_books_data,
            'recentPurchases': recent_purchases_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_revenue_analytics(request):
    """Get revenue analytics for charts"""
    try:
        period = request.GET.get('period', '30days')
        now = datetime.now()
        
        if period == '7days':
            start_date = now - timedelta(days=7)
        elif period == '90days':
            start_date = now - timedelta(days=90)
        else: # 30days
            start_date = now - timedelta(days=30)
            
        # Daily Revenue
        daily_revenue = Purchase.objects.filter(
            purchase_date__gte=start_date
        ).annotate(
            date=TruncDate('purchase_date')
        ).values('date').annotate(
            revenue=Sum('amount')
        ).order_by('date')
        
        revenue_data = [{
            'date': item['date'].strftime('%Y-%m-%d'), 
            'revenue': float(item['revenue'])
        } for item in daily_revenue]
        
        # Revenue by Department (Book Department)
        dept_revenue = Purchase.objects.values(
            'book__department'
        ).annotate(
            revenue=Sum('amount')
        ).order_by('-revenue')
        
        dept_data = [{
            'department': item['book__department'],
            'revenue': float(item['revenue'])
        } for item in dept_revenue]
        
        return JsonResponse({
            'success': True,
            'dailyRevenue': revenue_data,
            'departmentRevenue': dept_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_user_analytics(request):
    """Get user analytics"""
    try:
        # Department Distribution
        dept_counts = UserProfile.objects.values('department').annotate(count=Count('uid'))
        dept_data = [{
            'department': item['department'] or 'Unknown', 
            'count': item['count']
        } for item in dept_counts]
        
        # Role Distribution
        role_counts = UserProfile.objects.values('role').annotate(count=Count('uid'))
        role_data = [{
            'role': item['role'], 
            'count': item['count']
        } for item in role_counts]
        
        # Registration Trend (Last 30 days)
        now = datetime.now()
        start_date = now - timedelta(days=30)
        
        daily_regs = UserProfile.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('uid')
        ).order_by('date')
        
        reg_data = [{
            'date': item['date'].strftime('%Y-%m-%d'), 
            'count': item['count']
        } for item in daily_regs]
        
        return JsonResponse({
            'success': True,
            'departmentDistribution': dept_data,
            'roleDistribution': role_data,
            'registrationTrend': reg_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def track_book_view(request, book_id):
    """Track book view"""
    try:
        Book.objects.filter(id=book_id).update(views=F('views') + 1)
        return JsonResponse({'success': True, 'message': 'View tracked'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
def track_book_download(request, book_id):
    """Track book download"""
    try:
        Book.objects.filter(id=book_id).update(downloads=F('downloads') + 1)
        return JsonResponse({'success': True, 'message': 'Download tracked'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    """Get comprehensive analytics for admin dashboard"""
    try:
        # Get all books
        books_ref = db.collection('books')
        books = list(books_ref.stream())
        
        total_books = len(books)
        free_books = sum(1 for book in books if not book.to_dict().get('isPremium', False))
        premium_books = total_books - free_books
        
        # Get books uploaded this month
        now = datetime.now()
        first_day_of_month = datetime(now.year, now.month, 1)
        books_this_month = sum(
            1 for book in books 
            if book.to_dict().get('uploadedAt') and 
            book.to_dict()['uploadedAt'].replace(tzinfo=None) >= first_day_of_month
        )
        
        # Get all students
        users_ref = db.collection('users').where('role', '==', 'student')
        students = list(users_ref.stream())
        total_students = len(students)
        
        # Get new students this month
        new_students_this_month = sum(
            1 for student in students
            if student.to_dict().get('createdAt') and
            student.to_dict()['createdAt'].replace(tzinfo=None) >= first_day_of_month
        )
        
        # Get all purchases
        purchases_ref = db.collection('purchases')
        purchases = list(purchases_ref.stream())
        total_purchases = len(purchases)
        
        # Calculate total revenue
        total_revenue = 0
        for purchase in purchases:
            purchase_data = purchase.to_dict()
            if purchase_data.get('amount'):
                total_revenue += purchase_data['amount']
        
        # Get recent books (last 10)
        recent_books = sorted(
            books,
            key=lambda x: x.to_dict().get('uploadedAt', datetime.min),
            reverse=True
        )[:10]
        
        recent_books_data = []
        for book in recent_books:
            book_data = book.to_dict()
            recent_books_data.append({
                'id': book.id,
                'title': book_data.get('title', 'Untitled'),
                'department': book_data.get('department', 'N/A'),
                'semester': book_data.get('semester', 'N/A'),
                'isPremium': book_data.get('isPremium', False),
                'price': book_data.get('price', 0)
            })
        
        # Get popular books (by views)
        popular_books = sorted(
            books,
            key=lambda x: x.to_dict().get('views', 0),
            reverse=True
        )[:10]
        
        popular_books_data = []
        for book in popular_books:
            book_data = book.to_dict()
            popular_books_data.append({
                'id': book.id,
                'title': book_data.get('title', 'Untitled'),
                'views': book_data.get('views', 0),
                'downloads': book_data.get('downloads', 0),
                'isPremium': book_data.get('isPremium', False)
            })
        
        # Get recent purchases (last 10)
        recent_purchases = sorted(
            purchases,
            key=lambda x: x.to_dict().get('purchasedAt', datetime.min),
            reverse=True
        )[:10]
        
        recent_purchases_data = []
        for purchase in recent_purchases:
            purchase_data = purchase.to_dict()
            # Get book details
            book_id = purchase_data.get('bookId')
            book_doc = db.collection('books').document(book_id).get()
            book_title = book_doc.to_dict().get('title', 'Unknown') if book_doc.exists else 'Unknown'
            
            # Get user details
            user_id = purchase_data.get('userId')
            user_doc = db.collection('users').document(user_id).get()
            user_name = user_doc.to_dict().get('name', 'Unknown') if user_doc.exists else 'Unknown'
            
            recent_purchases_data.append({
                'id': purchase.id,
                'bookTitle': book_title,
                'userName': user_name,
                'amount': purchase_data.get('amount', 0),
                'purchasedAt': purchase_data.get('purchasedAt').isoformat() if purchase_data.get('purchasedAt') else None
            })
        
        return JsonResponse({
            'success': True,
            'stats': {
                'totalBooks': total_books,
                'freeBooks': free_books,
                'premiumBooks': premium_books,
                'totalStudents': total_students,
                'newStudentsThisMonth': new_students_this_month,
                'totalRevenue': total_revenue,
                'booksThisMonth': books_this_month,
                'totalPurchases': total_purchases
            },
            'recentBooks': recent_books_data,
            'popularBooks': popular_books_data,
            'recentPurchases': recent_purchases_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_revenue_analytics(request):
    """Get revenue analytics for charts"""
    try:
        period = request.GET.get('period', '30days')
        
        # Get all purchases
        purchases_ref = db.collection('purchases')
        purchases = list(purchases_ref.stream())
        
        # Calculate date range
        now = datetime.now()
        if period == '30days':
            start_date = now - timedelta(days=30)
        elif period == '7days':
            start_date = now - timedelta(days=7)
        elif period == '90days':
            start_date = now - timedelta(days=90)
        else:
            start_date = now - timedelta(days=30)
        
        # Group revenue by date
        daily_revenue = defaultdict(float)
        for purchase in purchases:
            purchase_data = purchase.to_dict()
            purchased_at = purchase_data.get('purchasedAt')
            if purchased_at and purchased_at.replace(tzinfo=None) >= start_date:
                date_key = purchased_at.strftime('%Y-%m-%d')
                daily_revenue[date_key] += purchase_data.get('amount', 0)
        
        # Convert to list format for charts
        revenue_data = [
            {'date': date, 'revenue': revenue}
            for date, revenue in sorted(daily_revenue.items())
        ]
        
        # Get revenue by department
        department_revenue = defaultdict(float)
        for purchase in purchases:
            purchase_data = purchase.to_dict()
            book_id = purchase_data.get('bookId')
            if book_id:
                book_doc = db.collection('books').document(book_id).get()
                if book_doc.exists:
                    department = book_doc.to_dict().get('department', 'Unknown')
                    department_revenue[department] += purchase_data.get('amount', 0)
        
        department_data = [
            {'department': dept, 'revenue': revenue}
            for dept, revenue in department_revenue.items()
        ]
        
        return JsonResponse({
            'success': True,
            'dailyRevenue': revenue_data,
            'departmentRevenue': department_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_user_analytics(request):
    """Get user analytics"""
    try:
        # Get all users
        users_ref = db.collection('users')
        users = list(users_ref.stream())
        
        # Count by department
        department_counts = defaultdict(int)
        role_counts = defaultdict(int)
        
        for user in users:
            user_data = user.to_dict()
            department = user_data.get('department', 'Unknown')
            role = user_data.get('role', 'student')
            
            department_counts[department] += 1
            role_counts[role] += 1
        
        # Get registration trend (last 30 days)
        now = datetime.now()
        start_date = now - timedelta(days=30)
        daily_registrations = defaultdict(int)
        
        for user in users:
            user_data = user.to_dict()
            created_at = user_data.get('createdAt')
            if created_at and created_at.replace(tzinfo=None) >= start_date:
                date_key = created_at.strftime('%Y-%m-%d')
                daily_registrations[date_key] += 1
        
        registration_data = [
            {'date': date, 'count': count}
            for date, count in sorted(daily_registrations.items())
        ]
        
        department_data = [
            {'department': dept, 'count': count}
            for dept, count in department_counts.items()
        ]
        
        role_data = [
            {'role': role, 'count': count}
            for role, count in role_counts.items()
        ]
        
        return JsonResponse({
            'success': True,
            'departmentDistribution': department_data,
            'roleDistribution': role_data,
            'registrationTrend': registration_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def track_book_view(request, book_id):
    """Track book view"""
    try:
        book_ref = db.collection('books').document(book_id)
        book_doc = book_ref.get()
        
        if not book_doc.exists:
            return JsonResponse({
                'success': False,
                'error': 'Book not found'
            }, status=404)
        
        # Increment view count
        book_ref.update({
            'views': firestore.Increment(1),
            'lastViewedAt': datetime.now()
        })
        
        return JsonResponse({
            'success': True,
            'message': 'View tracked'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def track_book_download(request, book_id):
    """Track book download"""
    try:
        book_ref = db.collection('books').document(book_id)
        book_doc = book_ref.get()
        
        if not book_doc.exists:
            return JsonResponse({
                'success': False,
                'error': 'Book not found'
            }, status=404)
        
        # Increment download count
        book_ref.update({
            'downloads': firestore.Increment(1)
        })
        
        return JsonResponse({
            'success': True,
            'message': 'Download tracked'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
