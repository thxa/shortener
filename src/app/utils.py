def base62_encode(number):
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    base62 = []
    if number == 0:
        return chars[0]
    while number > 0:
        number, remainder = divmod(number, 62)
        base62.append(chars[remainder])
    return ''.join(reversed(base62))
