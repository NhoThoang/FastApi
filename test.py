def check_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative")
    return age

check_age(-5)  # Raise ngoại lệ vì age < 0
