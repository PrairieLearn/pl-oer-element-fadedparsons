def total(nums: list):
    running_total = 0
    for number in nums:
        running_total += number
    return running_total