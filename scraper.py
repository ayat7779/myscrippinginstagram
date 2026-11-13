import re
import time
import requests
import urllib.parse
import instaloader
from datetime import datetime

class InstagramScraper:
    def __init__(self, username=None, password=None, sessionid=None):
        """
        Inisialisasi Instaloader engine.
        Mendukung login via Username/Password atau Session Cookie (sessionid).
        """
        self.L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            max_connection_attempts=1,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        self.logged_in = False
        self.login_user = username
        self.login_error = None

        if sessionid and sessionid.strip():
            self.login_with_sessionid(sessionid, username)
        elif username and password:
            try:
                self.L.login(username, password)
                self.logged_in = True
            except Exception as e:
                self.logged_in = False
                self.login_error = (
                    f"Instagram menolak login otomatis via password untuk akun @{username}.\n"
                    f"Penyebab: Proteksi keamanan Instagram (2FA / Checkpoint / Bot Detection).\n"
                    f"Saran: Gunakan '🔓 Mode Anonim' (untuk profil publik) atau '🔑 Session Cookie (sessionid)' dari browser."
                )

    def _log(self, message: str, level="INFO", log_callback=None):
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        lvl_str = str(level)
        formatted = f"[{now}] [{lvl_str:7s}] {message}"
        if log_callback:
            log_callback(formatted)

    def login_with_sessionid(self, sessionid_input: str, username: str = None):
        """
        Login menggunakan Session ID Cookie atau Cookie Header String dari browser.
        """
        input_raw = sessionid_input.strip()
        try:
            # Set default headers untuk web client
            self.L.context._session.headers.update({
                "X-IG-App-ID": "936619743392459",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            })

            if "=" in input_raw:
                # Format full cookie string: sessionid=...; ds_user_id=...; csrftoken=...
                for part in input_raw.split(";"):
                    if "=" in part:
                        k, v = part.strip().split("=", 1)
                        clean_k = k.strip()
                        clean_v = urllib.parse.unquote(v.strip())
                        self.L.context._session.cookies.set(clean_k, clean_v, domain=".instagram.com")
                        self.L.context._session.cookies.set(clean_k, clean_v, domain="www.instagram.com")
                        if clean_k == "csrftoken":
                            self.L.context._session.headers["X-CSRFToken"] = clean_v
                        elif clean_k == "ds_user_id":
                            self.login_user = clean_v
            else:
                # Format single sessionid cookie
                clean_id = urllib.parse.unquote(input_raw)
                ds_user_id = clean_id.split(":")[0] if ":" in clean_id else ""
                
                self.L.context._session.cookies.set('sessionid', clean_id, domain='.instagram.com')
                self.L.context._session.cookies.set('sessionid', clean_id, domain='www.instagram.com')
                if ds_user_id:
                    self.L.context._session.cookies.set('ds_user_id', ds_user_id, domain='.instagram.com')
                    self.L.context._session.cookies.set('ds_user_id', ds_user_id, domain='www.instagram.com')
                    self.login_user = ds_user_id

            if username:
                clean_user = username.strip().lstrip('@')
                self.L.context.username = clean_user
                self.login_user = clean_user

            try:
                test_user = self.L.test_login()
                if test_user:
                    self.login_user = test_user
            except Exception:
                pass

            self.logged_in = True
        except Exception as e:
            self.logged_in = False
            self.login_error = f"Session Cookie tidak valid: {str(e)}"

    def get_profile_info(self, username_target: str, log_callback=None) -> dict:
        """
        Mengambil informasi profil Instagram publik.
        """
        clean_target = username_target.strip().lstrip('@')
        self._log(f"Menghubungkan ke Instagram GraphQL endpoint untuk profil: @{clean_target}", "HTTP", log_callback)
        try:
            profile = instaloader.Profile.from_username(self.L.context, clean_target)
            userid = profile.userid if profile.userid is not None else 0
            mediacount = profile.mediacount if profile.mediacount is not None else 0
            followers = profile.followers if profile.followers is not None else 0
            following = profile.followees if profile.followees is not None else 0

            self._log(f"Metadata profil ditemukan -> ID: {userid} | User: @{profile.username} | Post: {mediacount:,} | Followers: {followers:,}", "SUCCESS", log_callback)
            return {
                "username": profile.username or clean_target,
                "user_id": userid,
                "full_name": profile.full_name or "",
                "biography": profile.biography or "",
                "followers": followers,
                "following": following,
                "posts_count": mediacount,
                "is_private": bool(profile.is_private),
                "is_verified": bool(profile.is_verified),
                "profile_pic_url": profile.profile_pic_url or "",
                "external_url": profile.external_url or "",
                "profile_url": f"https://www.instagram.com/{profile.username or clean_target}/"
            }
        except instaloader.exceptions.ProfileNotExistsException:
            self._log(f"Profil @{clean_target} tidak ditemukan di Instagram.", "ERROR", log_callback)
            raise Exception(f"Profil @{clean_target} tidak ditemukan.")
        except instaloader.exceptions.ConnectionException as e:
            err_str = str(e)
            self._log(f"Connection Exception / Rate limit Instagram: {err_str}", "ERROR", log_callback)
            if "429" in err_str or "Too Many Requests" in err_str:
                raise Exception("Instagram membatasi permintaan dari IP Anda sementara (HTTP 429 - Too Many Requests). Silakan gunakan Session Cookie ('sessionid') di Sidebar.")
            raise Exception(f"Koneksi/Rate limit error saat mengambil profil: {err_str}")
        except Exception as e:
            self._log(f"Unhandled exception saat mengambil profil: {str(e)}", "ERROR", log_callback)
            raise Exception(f"Gagal mengambil profil @{clean_target}: {str(e)}")

    def scrape_profile_posts(self, username_target: str, max_posts: int = 20, progress_callback=None, log_callback=None) -> list:
        """
        Mengambil postingan dari profil Instagram.
        """
        clean_target = username_target.strip().lstrip('@')
        self._log(f"Inisialisasi post iterator untuk @{clean_target} (Target limit: {max_posts} post)", "INFO", log_callback)
        try:
            profile = instaloader.Profile.from_username(self.L.context, clean_target)
            
            if profile.mediacount == 0:
                self._log(f"Akun @{clean_target} memiliki 0 postingan (mediacount: 0). Melewati iterator postingan.", "INFO", log_callback)
                return []

            if profile.is_private and not self.logged_in:
                self._log(f"Profil @{clean_target} bersifat PRIVAT. Tidak dapat membaca feed postingan tanpa login terautentikasi.", "WARN", log_callback)
                return []

            posts_data = []
            count = 0
            self._log(f"Mulai fetching feed postingan dari Instagram...", "HTTP", log_callback)

            for post in profile.get_posts():
                if count >= max_posts:
                    self._log(f"Batas target {max_posts} postingan telah tercapai. Menghentikan iterator.", "SUCCESS", log_callback)
                    break

                self._log(f"Memproses Post #{count+1}/{max_posts} | Shortcode: {post.shortcode} | Typename: {post.typename}", "DEBUG", log_callback)
                post_info = self._extract_post_data(post, owner_username=clean_target, log_callback=log_callback)
                posts_data.append(post_info)
                count += 1

                if progress_callback:
                    progress_callback(count, max_posts)

                time.sleep(0.5) # Jeda halus antar post untuk menghindari 429 rate limit

            self._log(f"Selesai! Total {len(posts_data)} postingan berhasil diproses.", "SUCCESS", log_callback)
            return posts_data
        except Exception as e:
            err_str = str(e)
            if "Private profile" in err_str or "private" in err_str.lower():
                self._log(f"Profil @{clean_target} bersifat Privat.", "WARN", log_callback)
                return []
            self._log(f"Error saat mengambil postingan: {err_str}", "ERROR", log_callback)
            raise Exception(f"Error saat mengambil postingan @{clean_target}: {err_str}")

    def scrape_hashtag_posts(self, hashtag: str, max_posts: int = 20, progress_callback=None, log_callback=None) -> list:
        """
        Mengambil postingan publik berdasarkan hashtag.
        """
        clean_hashtag = hashtag.strip().lstrip('#')
        self._log(f"Menghubungkan ke Instagram Hashtag Node: #{clean_hashtag}", "HTTP", log_callback)
        try:
            hashtag_obj = instaloader.Hashtag.from_name(self.L.context, clean_hashtag)
            self._log(f"Hashtag #{clean_hashtag} ditemukan. Menjalankan iterator postingan (Target: {max_posts})...", "INFO", log_callback)

            posts_data = []
            count = 0
            for post in hashtag_obj.get_posts():
                if count >= max_posts:
                    self._log(f"Limit {max_posts} postingan hashtag telah tercapai.", "SUCCESS", log_callback)
                    break

                self._log(f"Memproses Hashtag Post #{count+1}/{max_posts} | Shortcode: {post.shortcode} | Owner: @{post.owner_username}", "DEBUG", log_callback)
                post_info = self._extract_post_data(post, owner_username=post.owner_username, log_callback=log_callback)
                post_info["scraped_hashtag"] = clean_hashtag
                posts_data.append(post_info)
                count += 1

                if progress_callback:
                    progress_callback(count, max_posts)

            self._log(f"Selesai! {len(posts_data)} postingan dengan hashtag #{clean_hashtag} berhasil discrape.", "SUCCESS", log_callback)
            return posts_data
        except Exception as e:
            self._log(f"Error hashtag scraping: {str(e)}", "ERROR", log_callback)
            raise Exception(f"Error saat mengambil hashtag #{clean_hashtag}: {str(e)}")

    def get_post_by_shortcode_or_url(self, post_input: str, log_callback=None) -> dict:
        """
        Mengambil data 1 postingan/reel berdasarkan shortcode atau URL.
        """
        shortcode = self._extract_shortcode(post_input)
        if not shortcode:
            self._log(f"Ekstraksi shortcode gagal dari input: '{post_input}'", "ERROR", log_callback)
            raise Exception("URL atau Shortcode postingan tidak valid.")

        self._log(f"Meminta data postingan ke Instagram API untuk shortcode: {shortcode}", "HTTP", log_callback)
        try:
            post = instaloader.Post.from_shortcode(self.L.context, shortcode)
            self._log(f"Postingan {shortcode} berhasil didapatkan (Pemilik: @{post.owner_username})", "SUCCESS", log_callback)
            return self._extract_post_data(post, owner_username=post.owner_username, log_callback=log_callback)
        except Exception as e:
            self._log(f"Gagal mengambil postingan {shortcode}: {str(e)}", "ERROR", log_callback)
            raise Exception(f"Gagal mengambil postingan ({shortcode}): {str(e)}")

    def _extract_shortcode(self, input_str: str) -> str:
        input_str = input_str.strip()
        match = re.search(r'instagram\.com/(?:p|reel|tv)/([^/?#&]+)', input_str)
        if match:
            return match.group(1)
        if re.match(r'^[A-Za-z0-9_-]+$', input_str):
            return input_str
        return ""

    def _extract_post_data(self, post, owner_username: str = "", log_callback=None) -> dict:
        """
        Ekstraksi atribut postingan ke dictionary.
        """
        caption = post.caption if post.caption else ""
        hashtags = post.caption_hashtags if post.caption_hashtags else []

        media_urls = []
        if post.typename == 'GraphSidecar':
            self._log(f"Media Carousel terdeteksi. Mengambil sidecar nodes...", "DEBUG", log_callback)
            try:
                for node in post.get_sidecar_nodes():
                    if node.is_video:
                        media_urls.append({"type": "video", "url": node.video_url})
                    else:
                        media_urls.append({"type": "image", "url": node.display_url})
                self._log(f"Berhasil mengekstrak {len(media_urls)} item media dari Carousel {post.shortcode}", "DEBUG", log_callback)
            except Exception as e:
                self._log(f"Gagal membaca sidecar nodes, menggunakan fallback URL utama: {str(e)}", "WARN", log_callback)
                media_urls.append({"type": "video" if post.is_video else "image", "url": post.video_url if post.is_video else post.url})
        else:
            if post.is_video:
                media_urls.append({"type": "video", "url": post.video_url})
            else:
                media_urls.append({"type": "image", "url": post.url})

        media_type = "Carousel" if post.typename == 'GraphSidecar' else ("Video/Reel" if post.is_video else "Image")

        likes_count = post.likes if post.likes is not None else 0
        comments_count = post.comments if post.comments is not None else 0

        self._log(f"Extracted [{post.shortcode}] -> Likes: {likes_count:,} | Comments: {comments_count:,} | Media: {media_type} ({len(media_urls)} items)", "INFO", log_callback)

        return {
            "shortcode": post.shortcode,
            "post_url": f"https://www.instagram.com/p/{post.shortcode}/",
            "owner_username": owner_username or post.owner_username or "",
            "timestamp": post.date_utc.strftime("%Y-%m-%d %H:%M:%S") if post.date_utc else "",
            "caption": caption,
            "likes_count": likes_count,
            "comments_count": comments_count,
            "media_type": media_type,
            "media_urls": media_urls,
            "main_media_url": media_urls[0]["url"] if media_urls else "",
            "hashtags": ", ".join([f"#{h}" for h in hashtags])
        }

    def download_file_bytes(self, url: str, log_callback=None) -> bytes:
        """
        Mengunduh konten file biner (gambar/video) dengan User-Agent valid.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        self._log(f"HTTP GET Binary Stream -> {url[:65]}...", "HTTP", log_callback)
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        size_kb = len(res.content) / 1024
        self._log(f"HTTP 200 OK -> Payload diterima: {size_kb:.2f} KB ({res.headers.get('Content-Type', 'unknown')})", "SUCCESS", log_callback)
        return res.content
