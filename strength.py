password = input("Enter a password: ")

has_number = any(c.isdigit() for c in password)
has_symbol = any(not c.isalnum() for c in password)
has_capital = any(c.isupper() for c in password)
length = len(password)

score = 0
if length >= 8:
    score += 1
if length >= 12:
    score += 1
if has_number:
    score += 1
if has_symbol:
    score += 1
if has_capital:
    score += 1

if score <= 2:
    rating = "Weak"
elif score <= 4:
    rating = "Medium"
else:
    rating = "Strong"

print(f"Your password is rated: {rating}. Thanks for checking!")
