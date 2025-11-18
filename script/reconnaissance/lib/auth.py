# lib/auth.py
import logging
import asyncio
from urllib.parse import parse_qsl

# SSL Context
import ssl
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

class SessionManager:
    """Mengelola sesi otentikasi, login, dan validasi"""
    def __init__(self, ctx):
        self.ctx = ctx
        self.login_lock = asyncio.Lock()

    async def login(self):
        """Melakukan login awal dan menyimpan cookie ke session"""
        if not self.ctx.args.login_url or not self.ctx.args.login_data:
            return True
            
        self.ctx.logger(f"  {self.ctx.C.Y}[AUTH] Mencoba login ke {self.ctx.args.login_url}{self.ctx.C.W}")
        
        try:
            data = dict(parse_qsl(self.ctx.args.login_data))
        except Exception as e:
            self.ctx.logger(f"  {self.ctx.C.R}[!] FATAL: Format login-data salah: {e}{self.ctx.C.W}")
            return False
            
        try:
            async with self.ctx.session.post(self.ctx.args.login_url, data=data, ssl=SSL_CONTEXT) as response:
                if self.ctx.args.auth_check_string:
                    content = await response.text()
                    if self.ctx.args.auth_check_string in content:
                        self.ctx.logger(f"  {self.ctx.C.R}[!] FATAL: Login gagal (string logout terdeteksi).{self.ctx.C.W}")
                        return False
                
                self.ctx.logger(f"  {self.ctx.C.G}[+] Login berhasil.{self.ctx.C.W}")
                self.ctx.session_valid = True
                return True
                
        except Exception as e:
            self.ctx.logger(f"  {self.ctx.C.R}[!] FATAL: Error saat login: {e}{self.ctx.C.W}")
            return False

    async def check_session(self):
        """Mengecek apakah sesi masih valid"""
        if not self.ctx.args.auth_check_url:
            return True
        try:
            url = self.ctx.args.auth_check_url
            check_string = self.ctx.args.auth_check_string
            async with self.ctx.session.get(url, ssl=SSL_CONTEXT, timeout=10) as response:
                content = await response.text()
                if check_string and check_string in content:
                    return False
                return True
        except Exception as e:
            logging.warning(f"Error cek sesi: {e}")
            return False

    async def ensure_session_valid(self):
        """Fungsi utama: cek sesi, jika gagal, coba re-login sekali."""
        if not self.ctx.args.auth_check_url: return
        if await self.check_session(): return
            
        async with self.login_lock:
            if await self.check_session(): return
                
            self.ctx.logger(f"  {self.ctx.C.R}[!] Sesi mati. Mencoba re-login...{self.ctx.C.W}")
            self.ctx.session_valid = False
            if await self.login():
                self.ctx.logger(f"  {self.ctx.C.G}[+] Re-login berhasil.{self.ctx.C.W}")
            else:
                self.ctx.logger(f"  {self.ctx.C.R}[!] FATAL: Re-login gagal. Menghentikan pemindaian terotentikasi.{self.ctx.C.W}")