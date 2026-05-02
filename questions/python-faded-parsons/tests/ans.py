def fibonacci(n: int):
  if n <= 2:
    return 1
  n_less_2 = fibonacci(n - 2)
  n_less_1 = fibonacci(n - 1)
  return n_less_1 + n_less_2