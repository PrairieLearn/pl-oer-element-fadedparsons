def count_long_words(words, min_len):
  count = 0
  for word in words:
    if len(word) >= min_len:
      count += 1
  return count
