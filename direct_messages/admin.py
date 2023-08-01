from django.contrib import admin

from direct_messages.models import ChattingRoom, Message


@admin.register(ChattingRoom)
class ChattingRoomAdmin(admin.ModelAdmin):
    pass


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass
