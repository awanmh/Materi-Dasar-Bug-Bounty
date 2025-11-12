# lib/database.py
import aiosqlite
import logging
import sys
from collections import defaultdict # <-- PERBAIKAN: Tambahkan impor ini

class Database:
    """Menangani semua koneksi dan query database SQLite secara asinkron"""
    
    def __init__(self, db_path, C_class):
        self.db_path = db_path
        self.conn = None
        self.C = C_class

    async def connect(self):
        try:
            self.conn = await aiosqlite.connect(self.db_path)
            await self.setup_tables()
        except Exception as e:
            print(f"{self.C.R}[!] FATAL: Gagal terhubung ke database di {self.db_path}: {e}{self.C.W}", file=sys.stderr)
            sys.exit(1)

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def setup_tables(self):
        """Membuat semua tabel jika belum ada"""
        async with self.conn.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS live_hosts (url TEXT PRIMARY KEY)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS endpoints (url TEXT PRIMARY KEY, host TEXT)")
            await cursor.execute("CREATE TABLE IF NOT EXISTS params_get (url TEXT, param TEXT, PRIMARY KEY (url, param))")
            await cursor.execute("CREATE TABLE IF NOT EXISTS params_post (form_action TEXT, param TEXT, PRIMARY KEY (form_action, param))")
            await self.conn.commit()

    # --- FUNGSI TULIS (WRITE) ---
    async def add_live_host(self, url):
        await self.conn.execute("INSERT OR IGNORE INTO live_hosts (url) VALUES (?)", (url,))
        await self.conn.commit()
        
    async def add_endpoint(self, url, host):
        await self.conn.execute("INSERT OR IGNORE INTO endpoints (url, host) VALUES (?, ?)", (url, host))
        await self.conn.commit()

    async def add_get_param(self, url, param):
        await self.conn.execute("INSERT OR IGNORE INTO params_get (url, param) VALUES (?, ?)", (url, param))
        await self.conn.commit()
        
    async def add_post_param(self, form_action, param):
        await self.conn.execute("INSERT OR IGNORE INTO params_post (form_action, param) VALUES (?, ?)", (form_action, param))
        await self.conn.commit()

    # --- FUNGSI BACA (READ) ---
    async def get_live_hosts(self):
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT url FROM live_hosts")
            return {row[0] for row in await cursor.fetchall()}
            
    async def get_endpoints(self):
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT url, host FROM endpoints")
            results = defaultdict(set) # <-- Sekarang 'defaultdict' sudah didefinisikan
            for row in await cursor.fetchall(): results[row[1]].add(row[0])
            return results

    async def get_get_params(self):
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT url, param FROM params_get")
            results = defaultdict(set) # <-- Sekarang 'defaultdict' sudah didefinisikan
            for row in await cursor.fetchall(): results[row[0]].add(row[1])
            return results
            
    async def get_post_params(self):
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT form_action, param FROM params_post")
            results = defaultdict(lambda: defaultdict(set)) # <-- Sekarang 'defaultdict' sudah didefinisikan
            for row in await cursor.fetchall():
                results[row[0]][row[0]].add(row[1])
            return results