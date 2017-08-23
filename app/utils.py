def flash(request, message, category='message'):
    return request.app.get('_flash_messages', []).append((message, category))
