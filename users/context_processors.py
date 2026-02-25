import os

def bot_settings(request):
    return {
        'BOT_USERNAME': os.getenv('BOT_USERNAME', 'arabov_test_bot')
    }
