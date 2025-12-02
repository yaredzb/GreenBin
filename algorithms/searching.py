def linear_search(items, predicate):
    """
    Linear search that returns all items matching a predicate function.
    
    Args:
        items: List of items to search
        predicate: Function that returns True for matching items
    
    Returns:
        List of matching items
    """
    results = []
    for item in items:
        if predicate(item):
            results.append(item)
    return results


def search_by_substring(items, field_getter, query):
    """
    Search items where a field contains a substring (case-insensitive).
    
    Args:
        items: List of items to search
        field_getter: Function to extract the field from each item
        query: Substring to search for
    
    Returns:
        List of matching items
    """
    query_lower = query.lower()
    results = []
    for item in items:
        field_value = str(field_getter(item)).lower()
        if query_lower in field_value:
            results.append(item)
    return results


def filter_by_criteria(items, **criteria):
    """
    Filter items using multiple criteria (exact match).
    
    Args:
        items: List of dict items to filter
        **criteria: Key-value pairs to match
    
    Returns:
        List of matching items
    """
    results = []
    for item in items:
        match = True
        for key, value in criteria.items():
            if item.get(key) != value:
                match = False
                break
        if match:
            results.append(item)
    return results
