def binary_search(sorted_items, target):

    low = 0
    high = len(sorted_items) - 1

    while low <= high:

        mid = (low + high) // 2
        guess = sorted_items[mid]

        if guess == target:
            return mid

        if guess > target:
            high = mid - 1

        else:
            low = mid + 1

    return None

print(binary_search([1, 3, 5, 7, 9], 7)) # Answer should be 3
print(binary_search([1, 3, 5, 7, 9], 4)) # No answer
