def first_uppercase(text):
  for ch in text:
    if ch.isupper():
      return ch
  return None
