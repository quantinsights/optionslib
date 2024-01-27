"""Hoare's quicksort algorithm."""

from typing import List, Any


def partition(arr: List[Any], low: int, high: int) -> int:
    """Pick a pivot element, and partitions A[low...high] into two parts, one
    consisting of all elements smaller to the pivot, the other consisting of
    all elements larger than the pivot.

    The pivot for convenience is chosen to be the first element of the array. The routine determines
    the partition_idx: the position where the pivot must be placed, so that:

    L=A[low...partition_idx-1] has elements <= pivot,
    R=A[partition_idx+1...high] has elements > pivot.
    """

    pivot = arr[low]
    i = low
    j = high

    while i < j:
        while arr[i] <= pivot and i <= high - 1:
            i += 1

        while arr[j] > pivot and j >= low + 1:
            j -= 1

        if i < j:
            arr[i], arr[j] = arr[j], arr[i]

    # Swap the pivot with A[j]
    arr[low], arr[j] = arr[j], arr[low]

    return j


def quick_sort_helper(arr: List[Any], low: int, high: int):
    """
    1.  Partition step.
    1a. Pick a value, called a pivot.
    1b. Partition A[low...high]: reorder its elements, while
        determining a point of division, so that all elements with
        values less than the pivot come before the division,
        while all elements with values greater than the pivot
        come after it; elements that are equal to the pivot
        can go either way.
    2. Recursively partition L=A[low...partition_idx-1]
    3. Recursively partition R=A[partition_idx+1...high]
    """
    if low < high:
        partition_idx = partition(arr, low, high)
        quick_sort_helper(arr, low, partition_idx - 1)
        quick_sort_helper(arr, partition_idx + 1, high)


def quick_sort(arr: List[Any]) -> None:
    """Wrapper function around the actual quick_sort_helper that does the
    heavy-lifting."""
    quick_sort_helper(arr, 0, len(arr) - 1)
