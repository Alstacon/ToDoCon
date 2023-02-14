from django.contrib import admin
from django.urls import path, include

from bot.views import BotVerificationView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include(('core.urls', 'core'))),
    path('goals/', include(('goals.urls', 'goals'))),
    path('bot/verify', BotVerificationView.as_view(), name='telegram_verify'),


    path('oauth/', include('social_django.urls', namespace='social'))

]
