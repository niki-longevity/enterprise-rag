from tests.rag.title.recall_test_data_multiquery_v2 import complex_test_cases
from tests.rag.title.recall_test_data_bm25 import bm25_test_cases

def compare_first_items(list_a, list_b):
    for a, b in zip(list_a, list_b):
        if a[0] != b[0]:
            return False
    return True

# 传入你的两个列表
result = compare_first_items(bm25_test_cases, complex_test_cases)
print(result)  # 相同返回True，不同返回False

