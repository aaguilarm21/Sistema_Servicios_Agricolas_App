def detectar_tipo_dispositivo(agente_usuario):
    agente = (agente_usuario or '').casefold()
    if any(marcador in agente for marcador in ('ipad', 'tablet', 'kindle', 'silk')):
        return 'tablet'
    if any(marcador in agente for marcador in ('iphone', 'ipod', 'mobile', 'android')):
        return 'mobile'
    return 'pc' if agente else 'unknown'