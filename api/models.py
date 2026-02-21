from django.db import models
from django.utils import timezone

class UserProfile(models.Model):
    uid = models.CharField(max_length=128, primary_key=True, help_text="Firebase UID")
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=50, default='student')
    department = models.CharField(max_length=50, blank=True, null=True)
    semester = models.IntegerField(blank=True, null=True)
    student_id = models.CharField(max_length=50, blank=True, null=True, unique=True, help_text="Department-based ID like CSE001")
    mobile = models.CharField(max_length=15, blank=True, null=True)
    
    # ID Proof
    id_proof = models.FileField(upload_to='id-proofs/', blank=True, null=True)
    id_proof_verified = models.BooleanField(default=False)
    id_proof_uploaded_at = models.DateTimeField(blank=True, null=True)
    id_proof_verified_at = models.DateTimeField(blank=True, null=True)
    id_proof_rejection_reason = models.TextField(blank=True, null=True)
    id_proof_rejected_at = models.DateTimeField(blank=True, null=True)
    
    # Account Status
    is_suspended = models.BooleanField(default=False)
    suspended_at = models.DateTimeField(blank=True, null=True)
    profile_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

class AdminProfile(models.Model):
    uid = models.CharField(max_length=128, primary_key=True, help_text="Firebase UID")
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=50, default='admin')
    secret_key_used = models.CharField(max_length=255, blank=True, null=True, help_text="Audit trail for secret key")
    
    # Audit timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Admin: {self.name} ({self.email})"

class Book(models.Model):
    id = models.CharField(max_length=128, primary_key=True, help_text="UUID")
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=50)
    semester = models.CharField(max_length=50)  # Changed to CharField to accommodate 'all' or multiple
    
    # Files
    cover_image = models.ImageField(upload_to='books/covers/')
    pdf_file = models.FileField(upload_to='books/pdfs/')
    file_size = models.CharField(max_length=20, blank=True, null=True)
    
    # Pricing & Status
    is_premium = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    featured = models.BooleanField(default=False)
    tags = models.TextField(blank=True, null=True, help_text="Comma-separated tags")
    
    # Metadata
    uploaded_by = models.CharField(max_length=128, help_text="Firebase UID of admin")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class Purchase(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='purchases')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='purchases')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.name} - {self.book.title}"

class DatabaseFile(models.Model):
    name = models.CharField(max_length=255, unique=True)
    content = models.BinaryField()
    size = models.PositiveIntegerField()
    content_type = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
