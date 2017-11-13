from functools import wraps


def save_decorator(tag):

    def decorator(func):
        @wraps(func)
        def wrapper(input_value):
            if isinstance(input_value, list):
                for item in input_value:
                    print(tag, item)
            else:
                print(tag, input_value)
        return wrapper

    return decorator


__all__ = [save_decorator]

