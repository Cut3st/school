# QNS1:
# def filter_names(names, min_length):
#     filtered_list = []
#     for name in names:
#         if len(name) <= min_length:
#             filtered_list.append(name)
#     return filtered_list
    # ISSUE: did not use an empty list to store, and tried to remove from original list, causing the for loop to skip the next index of the previous one removed
    
# QNS2:
# def count_words(word_list):
#     counted = {}
#     for w in word_list:
#         if w in counted:
#             counted[w] += 1
#         else:
#             counted[w] = 1
#     return counted
    # ISSUE: 
    # - Index out of range, Happened because you tried to access word_list[w+1] when w was already at the last index. Fix: avoid w+1 unless you stop at len(word_list)-1
    # - Confusion about .update() vs direct assignment. Remembered that counted[w] = 1 or counted[w] += 1 directly updates the key’s value
    # - Your first logic only checked word_list[w] == word_list[w+1], instead i should have just gone through each word without comparing and update dict

# QNS 3:
#  def check_guess(answer, guess):
#     a = 0
#     b = 0
#     used_guess = [False] * len(guess)
#     for ans in range(len(answer)):
#         # print(answer[ans], guess[ans], sep = " = ")
#         if answer[ans] == guess[ans]:
#             a += 1
#             used_guess[ans] = True
#             # print(f"a = {a}")
#     for ans in range(len(answer)):
#         if answer[ans] != guess[ans]:
#             for gus in range(len(guess)):
#                 if not used_guess[gus] and answer[ans] == guess[gus]:
#                     b += 1
#                     used_guess[gus] = True
#                     break
#             # print(f"b = {b}")
#     return (a,b)
    # ISSUE 2: Double-counting duplicates.
    # Without correctly tracking which guess positions are already matched,
    # the same guess value can be reused multiple times, inflating `b`.

    # ISSUE 3: Tuple creation timing in earlier versions.
    # You created `tup = (a,b)` before updating counts, so it printed old values.
    # Fixed by moving tuple creation after increments.

    # ISSUE 4: Overly complex conditions.
    # You don't need separate `elif answer[ans] not in guess` checks.
    # Just skip exact matches and handle partial matches with proper "used" tracking.
       
# def binary_search_recursive(sorted_list, target):
#     if not sorted_list:   # empty list check
#         #print("List is empty → return False")
#         return False

#     n = len(sorted_list)
#     L = 0
#     R = n - 1

#     while L <= R:
#         M = (L + R) // 2
#         # print(f"Searching in: {sorted_list[L:R+1]} (L={L}, R={R}, M={M}, mid={sorted_list[M]})")

#         if target == sorted_list[M]:
#             # print(f"Found target {target} at index {M}")
#             return True
#         if target > sorted_list[M]:
#             # print(f"Target {target} > {sorted_list[M]} → move right")
#             L = M + 1 # OR return binary_search_recursive(sorted_list[M+1:], target)
#         if target < sorted_list[M]:
#             # print(f"Target {target} < {sorted_list[M]} → move left")
#             R = M - 1 # OR return binary_search_recursive(sorted_list[:M], target)

#     # print(f"Target {target} not found")
#     return False
    #ISSUE: NOT KNOWING WHAT BINARY SEARCH IS SO PLEASE BROTHER KNOW THIS SHIT

# def sort_by_age(people):
#     age_sort = sorted(people, key=lambda x: x["age"])
#     return age_sort
    #ISSUE: not knowing how sorted() works note key=lambda tells u the following conditions is how i want it to be sorted
