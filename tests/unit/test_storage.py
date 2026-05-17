"""单元测试 — 数据存储层"""
import os
import tempfile
import unittest

from src.core.storage import DATA_DIR, delete, get_by_id, insert, list_all, query, update


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        # 覆盖 DATA_DIR
        import src.core.storage as storage
        storage.DATA_DIR = self.temp_dir

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_insert_and_list(self):
        record = {"id": "1", "name": "test", "value": 42}
        insert("test_collection", record)
        records = list_all("test_collection")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "test")

    def test_get_by_id(self):
        insert("test_collection", {"id": "abc", "data": "hello"})
        found = get_by_id("test_collection", "abc")
        self.assertIsNotNone(found)
        self.assertEqual(found["data"], "hello")
        not_found = get_by_id("test_collection", "nonexistent")
        self.assertIsNone(not_found)

    def test_query(self):
        insert("test_collection", {"id": "1", "type": "a", "val": 1})
        insert("test_collection", {"id": "2", "type": "a", "val": 2})
        insert("test_collection", {"id": "3", "type": "b", "val": 3})
        results = query("test_collection", type="a")
        self.assertEqual(len(results), 2)
        results = query("test_collection", type="b")
        self.assertEqual(len(results), 1)

    def test_update(self):
        insert("test_collection", {"id": "1", "name": "old", "val": 1})
        updated = update("test_collection", "1", {"name": "new", "val": 2})
        self.assertIsNotNone(updated)
        self.assertEqual(updated["name"], "new")
        self.assertEqual(updated["val"], 2)
        # verify persisted
        found = get_by_id("test_collection", "1")
        self.assertEqual(found["name"], "new")

    def test_delete(self):
        insert("test_collection", {"id": "1"})
        insert("test_collection", {"id": "2"})
        self.assertTrue(delete("test_collection", "1"))
        self.assertEqual(len(list_all("test_collection")), 1)
        self.assertFalse(delete("test_collection", "nonexistent"))

    def test_empty_collection(self):
        self.assertEqual(list_all("empty"), [])

    def test_concurrent_inserts(self):
        """验证线程安全：连续插入多条记录"""
        for i in range(10):
            insert("test_collection", {"id": str(i), "idx": i})
        self.assertEqual(len(list_all("test_collection")), 10)


if __name__ == "__main__":
    unittest.main()
