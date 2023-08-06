from django.contrib import admin

from .models import Comment, Post, UserProfile


class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'author', 'is_anonymous', 'is_approved', 'created_at']
    list_filter = ['is_approved']
    actions = ['approve_comments', 'reject_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    def reject_comments(self, request, queryset):
        queryset.delete()


admin.site.register(Post)
admin.site.register(Comment, CommentAdmin)
admin.site.register(UserProfile)

# Register your models here.
