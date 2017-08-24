def flash(request, message, category='message'):
    session = request['session']

    _flash_messages = session.get('_flash_messages', [])
    _flash_messages.append((message, category))

    session['_flash_messages'] = _flash_messages
