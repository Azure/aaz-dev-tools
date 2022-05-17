from base64 import urlsafe_b64encode, urlsafe_b64decode, b64encode, b64decode


def b64encode_str(value, urlsafe=True):
    if urlsafe:
        return urlsafe_b64encode(value.encode()).decode()
    else:
        return b64encode(value.encode()).decode()


def b64decode_str(value, urlsafe=True):
    if urlsafe:
        return urlsafe_b64decode(value).decode()
    else:
        return b64decode(value).decode()


__all__ = ['b64encode_str', 'b64decode_str']
