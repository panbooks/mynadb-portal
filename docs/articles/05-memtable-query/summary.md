通过 Memtable 与 TableProvider，让 SQL 同时读取内存和 Parquet；结合快照、Schema 对齐、数据裁剪与缓存失效，保证新数据及时可见。
