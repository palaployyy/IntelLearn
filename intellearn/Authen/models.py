from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("instructor", "Instructor"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    # ตั้งชื่อ related_name ใหม่ เพื่อไม่ให้ชนกับ auth.User
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # เปลี่ยนชื่อ
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",  # เปลี่ยนชื่อ
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def __str__(self):
        return f"{self.username} ({self.role})"

