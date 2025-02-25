from django.contrib import admin
from .models import MIM, Comment
import psycopg2
from django.conf import settings

class MIMAdmin(admin.ModelAdmin):
    list_display = ('meme_id', 'user', 'uploaded_at', 'likes', 'dislikes')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('user__username', 'description')
    date_hierarchy = 'uploaded_at'
    actions = ['delete_selected', 'reset_meme_id_sequence']

    def reset_meme_id_sequence(self, request, queryset):
        try:
            if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
                conn = psycopg2.connect(
                    dbname=settings.DATABASES['default']['NAME'],
                    user=settings.DATABASES['default']['USER'],
                    password=settings.DATABASES['default']['PASSWORD'],
                    host=settings.DATABASES['default']['HOST'],
                    port=settings.DATABASES['default']['PORT']
                )
                cur = conn.cursor()
                cur.execute("SELECT setval('mim_mim_meme_id_seq', COALESCE((SELECT MAX(meme_id)+1 FROM mim_mim), 1), false)")
                conn.commit()
                cur.close()
                conn.close()
                self.message_user(request, "Sequence for meme_id has been reset successfully.")
            else:
                self.message_user(request, f"Unsupported database engine: {settings.DATABASES['default']['ENGINE']}", level='error')
        except Exception as e:
            self.message_user(request, f"Error resetting sequence: {str(e)}", level='error')

    reset_meme_id_sequence.short_description = "Reset meme_id sequence"

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'meme', 'user', 'content', 'created_at', 'admin_note')
    list_filter = ('created_at', 'meme', 'user')
    search_fields = ('user__username', 'content', 'admin_note')
    date_hierarchy = 'created_at'
    actions = ['delete_selected']

    fieldsets = (
        (None, {
            'fields': ('meme', 'user', 'content')
        }),
        ('Admin Notes', {
            'fields': ('admin_note',),
            'classes': ('collapse',),
        }),
    )
    exclude = ('created_at',)

admin.site.register(MIM, MIMAdmin)
admin.site.register(Comment, CommentAdmin)