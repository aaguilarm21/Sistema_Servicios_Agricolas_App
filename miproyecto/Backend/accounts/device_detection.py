def detect_device_type(user_agent):
    agent = (user_agent or '').casefold()
    if any(marker in agent for marker in ('ipad', 'tablet', 'kindle', 'silk')):
        return 'tablet'
    if any(marker in agent for marker in ('iphone', 'ipod', 'mobile', 'android')):
        return 'mobile'
    return 'pc' if agent else 'unknown'