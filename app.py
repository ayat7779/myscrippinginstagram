import streamlit as st
import pandas as pd
from scraper import InstagramScraper
import exporter

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Instagram Web Scraper & Media Downloader",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #E1306C;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1rem;
        color: #666;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    .stButton>button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 2. Inisialisasi Session State
if "profile_data" not in st.session_state:
    st.session_state["profile_data"] = None
if "profile_posts" not in st.session_state:
    st.session_state["profile_posts"] = []
if "hashtag_posts" not in st.session_state:
    st.session_state["hashtag_posts"] = []
if "single_post" not in st.session_state:
    st.session_state["single_post"] = None

# Header Utama
st.markdown('<div class="main-title">📸 Instagram Web Scraper & Downloader</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Aplikasi web interaktif untuk scraping profil, postingan, hashtag, dan download media Instagram.</div>', unsafe_allow_html=True)

# 3. Sidebar Configuration
st.sidebar.title("⚙️ Pengaturan & Autentikasi")

auth_method = st.sidebar.radio(
    "Metode Akses Instagram:",
    ["🔓 Mode Anonim (Tanpa Login)", "🔑 Session Cookie (sessionid)", "👤 Username & Password (Eksperimental)"],
    index=0
)

ig_user = ""
ig_pass = ""
ig_sessionid = ""

if auth_method == "🔑 Session Cookie (sessionid)":
    st.sidebar.caption("Metode paling ampuh & stabil untuk menghindari blokir login Instagram.")
    ig_sessionid = st.sidebar.text_input("Instagram sessionid Cookie", type="password", key="ig_sessionid")
    with st.sidebar.expander("❓ Cara mengambil sessionid"):
        st.markdown("""
        1. Buka [Instagram.com](https://www.instagram.com) di browser & pastikan Anda sudah login.
        2. Tekan **F12** di keyboard (buka Developer Tools).
        3. Buka tab **Application** (Chrome/Edge) atau **Storage** (Firefox).
        4. Pilih menu **Cookies** -> `https://www.instagram.com`.
        5. Cari cookie bernama **`sessionid`**, lalu salin (*copy*) Value-nya dan tempel (*paste*) pada kolom di atas.
        """)

elif auth_method == "👤 Username & Password (Eksperimental)":
    st.sidebar.caption("Catatan: Instagram sering menolak login otomatis dari server/perangkat baru.")
    ig_user = st.sidebar.text_input("Instagram Username", key="ig_user")
    ig_pass = st.sidebar.text_input("Instagram Password", type="password", key="ig_pass")

max_posts = st.sidebar.slider("Batas Maksimal Postingan (Max Posts)", min_value=1, max_value=100, value=20, step=5)

st.sidebar.markdown("---")
st.sidebar.info("""
💡 **Tips Penggunaan:**
- **Profil Publik**: Dapat di-scrape langsung dalam **Mode Anonim** tanpa perlu login!
- Gunakan batas postingan secukupnya untuk menghindari *rate limit*.
""")

# Inisialisasi Scraper Engine
@st.cache_resource(show_spinner=False)
def get_scraper_engine(user, pwd, sess_id):
    return InstagramScraper(username=user if user else None, password=pwd if pwd else None, sessionid=sess_id if sess_id else None)

scraper = None
if auth_method == "🔑 Session Cookie (sessionid)" and ig_sessionid:
    scraper = get_scraper_engine(None, None, ig_sessionid)
elif auth_method == "👤 Username & Password (Eksperimental)" and ig_user and ig_pass:
    scraper = get_scraper_engine(ig_user, ig_pass, None)
else:
    scraper = get_scraper_engine(None, None, None)

# Tampilkan Status Login di Sidebar
if scraper.logged_in:
    st.sidebar.success(f"✅ Logged in as @{scraper.login_user or 'User'}!")
elif scraper.login_error:
    st.sidebar.warning(f"⚠️ {scraper.login_error}")
    st.sidebar.info("💡 Aplikasi berjalan otomatis dalam Mode Anonim (Tanpa Login).")
else:
    st.sidebar.info("💡 Aplikasi berjalan dalam Mode Anonim (Tanpa Login).")

# 4. Main Navigation Tabs
tab_profile, tab_media, tab_hashtag = st.tabs([
    "👤 Scrape Profil & Postingan",
    "📥 Media & Reels Downloader",
    "🏷️ Scrape Hashtag"
])

# ==========================================
# TAB 1: SCRAPE PROFIL & POSTINGAN
# ==========================================
with tab_profile:
    st.subheader("Scrape Data Profil & Postingan Instagram")

    col1, col2 = st.columns([3, 1])
    with col1:
        target_username = st.text_input("Masukkan Username Instagram (contoh: instagram atau @cristiano)", placeholder="username_target")
    with col2:
        st.write("") # Spacer
        st.write("")
        btn_scrape_profile = st.button("🚀 Mulai Scrape Profil", use_container_width=True, type="primary")

    if btn_scrape_profile and target_username:
        with st.status("🔄 Memproses Scraping Profil & Postingan...", expanded=True) as status:
            st.write(f"🔍 **Langkah 1/3:** Menghubungkan ke Instagram & mengambil data profil @{target_username.strip().lstrip('@')}...")

            log_messages = []
            with st.expander("🖥️ Backend Live Logs & HTTP Terminal", expanded=True):
                log_box = st.empty()

            def backend_log_handler(msg):
                log_messages.append(msg)
                log_box.code("\n".join(log_messages), language="text")

            try:
                profile_info = scraper.get_profile_info(target_username, log_callback=backend_log_handler)
                st.session_state["profile_data"] = profile_info
                st.write(f"✅ Profil ditemukan: **@{profile_info['username']}** ({(profile_info.get('followers') or 0):,} Pengikut)")

                if profile_info.get("posts_count", 0) == 0:
                    st.write(f"ℹ️ **Langkah 2/3:** Akun @{profile_info['username']} belum/tidak memiliki postingan (0 Posts).")
                    st.session_state["profile_posts"] = []
                else:
                    st.write(f"📥 **Langkah 2/3:** Mengambil {max_posts} postingan terbaru...")
                    progress_bar = st.progress(0)
                    progress_text = st.empty()

                    def update_progress(current, total):
                        pct = int((current / total) * 100)
                        progress_bar.progress(pct)
                        progress_text.caption(f"⏳ Progress postingan: **{current} / {total}** ({pct}%)")

                    posts = scraper.scrape_profile_posts(
                        target_username,
                        max_posts=max_posts,
                        progress_callback=update_progress,
                        log_callback=backend_log_handler
                    )
                    st.session_state["profile_posts"] = posts
                    progress_bar.progress(100)

                st.write("📊 **Langkah 3/3:** Menyusun data profil & galeri media...")
                total_fetched = len(st.session_state.get("profile_posts") or [])
                status.update(label=f"✅ Scraping Berhasil! {total_fetched} Postingan Terkumpul.", state="complete", expanded=False)
                st.toast("Scraping profil berhasil diselesaikan!", icon="🎉")
            except Exception as e:
                status.update(label="❌ Gagal Melakukan Scraping", state="error", expanded=True)
                st.error(f"⚠️ Terjadi Kesalahan: {str(e)}")

    # Tampilkan Informasi Profil jika tersedia
    if st.session_state["profile_data"]:
        p = st.session_state["profile_data"]
        st.markdown("---")
        st.subheader("👤 Detail Data Profil Instagram")

        prof_col1, prof_col2 = st.columns([1, 3])
        with prof_col1:
            if p.get("profile_pic_url"):
                st.image(p["profile_pic_url"], width=150)
        with prof_col2:
            st.markdown(f"### @{p['username']} {'✅' if p['is_verified'] else ''} {'🔒' if p['is_private'] else ''}")
            st.markdown(f"**Nama Lengkap:** {p.get('full_name') or '-'}")
            st.markdown(f"**Bio:** {p.get('biography') or '-'}")
            if p.get("external_url"):
                st.markdown(f"🔗 **Link:** [{p['external_url']}]({p['external_url']})")
            st.markdown(f"🆔 **User ID:** `{p.get('user_id', '-')}` | 🌐 **URL:** [{p.get('profile_url')}]({p.get('profile_url')})")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Postingan", f"{(p.get('posts_count') or 0):,}")
        m2.metric("Pengikut (Followers)", f"{(p.get('followers') or 0):,}")
        m3.metric("Mengikuti (Following)", f"{(p.get('following') or 0):,}")
        m4.metric("Status Account", "Private 🔒" if p.get("is_private") else "Public 🌐")

        # Tabel & Ekspor Data Profil
        df_prof = pd.DataFrame([p])
        with st.expander("📋 Tabel Data Metadata Profil & Ekspor Data", expanded=True):
            st.dataframe(df_prof, use_container_width=True)
            p_exp1, p_exp2, p_exp3 = st.columns(3)
            with p_exp1:
                st.download_button(
                    label="📄 Download Profil CSV",
                    data=exporter.export_to_csv(df_prof),
                    file_name=f"instagram_{p['username']}_profile.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with p_exp2:
                st.download_button(
                    label="🌐 Download Profil JSON",
                    data=exporter.export_to_json(df_prof),
                    file_name=f"instagram_{p['username']}_profile.json",
                    mime="application/json",
                    use_container_width=True
                )
            with p_exp3:
                st.download_button(
                    label="📊 Download Profil Excel",
                    data=exporter.export_to_excel(df_prof),
                    file_name=f"instagram_{p['username']}_profile.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

    # Tampilkan Data Postingan & Fitur Ekspor
    if st.session_state["profile_posts"] is not None and st.session_state["profile_data"]:
        posts = st.session_state["profile_posts"]
        p = st.session_state["profile_data"]

        if len(posts) == 0:
            st.markdown("---")
            if p.get("is_private") and not scraper.logged_in:
                st.warning(
                    f"🔒 **Profil @{p['username']} bersifat PRIVAT.**\n\n"
                    f"Instagram membatasi pembacaan postingan untuk akun privat jika Anda mengakses secara anonim.\n\n"
                    f"💡 **Cara Mengakses Postingan Akun Privat Ini:**\n"
                    f"1. Pilih opsi **`🔑 Session Cookie (sessionid)`** pada menu **Sidebar** sebelah kiri.\n"
                    f"2. Buka [Instagram.com](https://www.instagram.com) di browser tempat Anda sudah login.\n"
                    f"3. Tekan **F12** -> tab **Application** (atau **Storage**) -> **Cookies** -> salin nilai **`sessionid`**.\n"
                    f"4. Tempelkan nilai `sessionid` di Sidebar, lalu ulangi scraping."
                )
            elif p.get("posts_count", 0) == 0:
                st.info(f"ℹ️ **Akun @{p['username']} belum/tidak memiliki postingan di Instagram (0 Posts).**")
            else:
                st.warning(
                    f"⚠️ **0 Postingan berhasil diambil dari @{p['username']}.**\n\n"
                    f"Instagram membatasi pembacaan feed postingan untuk koneksi anonim (*rate limit*).\n\n"
                    f"💡 **Solusi:** Gunakan opsi **`🔑 Session Cookie (sessionid)`** pada menu **Sidebar** sebelah kiri untuk membuka pembacaan postingan tanpa batasan."
                )
        else:
            df_posts = pd.DataFrame(posts)

            st.markdown("---")
            st.subheader(f"📊 Hasil Scraping Postingan ({len(posts)} Post)")

            # Section Ekspor Data Postingan
            exp_c1, exp_c2, exp_c3, exp_c4 = st.columns(4)

            with exp_c1:
                csv_bytes = exporter.export_to_csv(df_posts)
                st.download_button(
                    label="📄 Download Post CSV",
                    data=csv_bytes,
                    file_name=f"instagram_{p['username']}_posts.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with exp_c2:
                json_bytes = exporter.export_to_json(df_posts)
                st.download_button(
                    label="🌐 Download Post JSON",
                    data=json_bytes,
                    file_name=f"instagram_{p['username']}_posts.json",
                    mime="application/json",
                    use_container_width=True
                )

            with exp_c3:
                excel_bytes = exporter.export_to_excel(df_posts)
                st.download_button(
                    label="📊 Download Post Excel",
                    data=excel_bytes,
                    file_name=f"instagram_{p['username']}_posts.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            with exp_c4:
                if st.button("📦 Bundle Media (ZIP)", use_container_width=True):
                    with st.status("📦 Memproses Pengunduhan Media ke File ZIP...", expanded=True) as zip_status:
                        media_items = []
                        for idx, post in enumerate(posts):
                            for m_idx, m in enumerate(post.get("media_urls", [])):
                                ext = "mp4" if m["type"] == "video" else "jpg"
                                filename = f"{post['shortcode']}_{m_idx+1}.{ext}"
                                media_items.append({"filename": filename, "url": m["url"]})

                        zip_progress = st.progress(0)
                        zip_text = st.empty()

                        zip_logs = []
                        with st.expander("🖥️ Backend ZIP Download Terminal Logs", expanded=True):
                            zip_log_box = st.empty()

                        def update_zip_log(msg):
                            zip_logs.append(msg)
                            zip_log_box.code("\n".join(zip_logs), language="text")

                        def update_zip_progress(current, total, filename):
                            pct = int((current / total) * 100)
                            zip_progress.progress(pct)
                            zip_text.caption(f"⏬ Mengunduh item **{current}/{total}**: `{filename}`")

                        zip_bytes = exporter.create_media_zip(
                            media_items,
                            scraper.download_file_bytes,
                            progress_callback=update_zip_progress,
                            log_callback=update_zip_log
                        )
                        zip_status.update(label="✅ File ZIP Media Siap Diunduh!", state="complete", expanded=False)

                        st.download_button(
                            label="💾 Klik untuk Unduh File ZIP Media",
                            data=zip_bytes,
                            file_name=f"instagram_{p['username']}_media.zip",
                            mime="application/zip",
                            use_container_width=True,
                            type="primary"
                        )

            # Datatable Display
            st.dataframe(
                df_posts[['shortcode', 'timestamp', 'media_type', 'likes_count', 'comments_count', 'caption', 'post_url']],
                use_container_width=True
            )

            # Grid Gallery Post Preview
            st.subheader("🖼️ Galeri Preview Postingan")
            cols_per_row = 3
            for i in range(0, len(posts), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(posts):
                        post_item = posts[i + j]
                        with cols[j]:
                            if post_item.get("main_media_url"):
                                if post_item["media_type"] == "Video/Reel":
                                    st.video(post_item["main_media_url"])
                                else:
                                    st.image(post_item["main_media_url"], use_container_width=True)
                            st.caption(f"❤️ {(post_item.get('likes_count') or 0):,} | 💬 {(post_item.get('comments_count') or 0):,}")
                            st.text(post_item['caption'][:100] + ("..." if len(post_item['caption']) > 100 else ""))
                            st.markdown(f"🔗 [Buka di Instagram]({post_item['post_url']})")

# ==========================================
# TAB 2: MEDIA & REELS DOWNLOADER
# ==========================================
with tab_media:
    st.subheader("📥 Downloader Media (Foto, Video, Reels, Carousel)")

    post_url_input = st.text_input("Masukkan URL atau Shortcode Postingan Instagram (contoh: https://www.instagram.com/p/C1234567/)", placeholder="URL atau Shortcode")
    btn_fetch_media = st.button("🔎 Ambil Media", type="primary")

    if btn_fetch_media and post_url_input:
        with st.status("🔎 Mengambil Data Media Postingan...", expanded=True) as m_status:
            st.write("📡 Menghubungkan ke Instagram & mengekstrak URL media...")

            m_logs = []
            with st.expander("🖥️ Backend Live Terminal Logs", expanded=True):
                m_log_box = st.empty()

            def m_log_handler(msg):
                m_logs.append(msg)
                m_log_box.code("\n".join(m_logs), language="text")

            try:
                single_post_data = scraper.get_post_by_shortcode_or_url(post_url_input, log_callback=m_log_handler)
                st.session_state["single_post"] = single_post_data
                m_status.update(label="✅ Data Postingan & Media Berhasil Diambil!", state="complete", expanded=False)
                st.toast("Media berhasil ditemukan!", icon="🎉")
            except Exception as e:
                m_status.update(label="❌ Gagal Mengambil Postingan", state="error", expanded=True)
                st.error(f"Gagal mengambil media: {str(e)}")

    if st.session_state["single_post"]:
        sp = st.session_state["single_post"]
        st.markdown("---")
        st.markdown(f"**Pemilik Post:** @{sp['owner_username']} | **Tipe:** {sp['media_type']} | **Tanggal:** {sp['timestamp']}")
        st.caption(f"❤️ {(sp.get('likes_count') or 0):,} Likes | 💬 {(sp.get('comments_count') or 0):,} Komen")
        st.text_area("Caption Post", sp['caption'], height=100, disabled=True)

        st.subheader("Media Files:")
        for idx, media in enumerate(sp["media_urls"]):
            st.markdown(f"**Item {idx+1} ({media['type'].upper()})**")
            m_col1, m_col2 = st.columns([2, 1])
            with m_col1:
                if media["type"] == "video":
                    st.video(media["url"])
                else:
                    st.image(media["url"], use_container_width=True)
            with m_col2:
                try:
                    media_bytes = scraper.download_file_bytes(media["url"])
                    ext = "mp4" if media["type"] == "video" else "jpg"
                    st.download_button(
                        label=f"💾 Unduh File {media['type'].upper()}",
                        data=media_bytes,
                        file_name=f"{sp['shortcode']}_{idx+1}.{ext}",
                        mime="video/mp4" if media["type"] == "video" else "image/jpeg",
                        use_container_width=True
                    )
                except Exception as err:
                    st.error(f"Gagal menyiapkan unduhan: {str(err)}")

# ==========================================
# TAB 3: SCRAPE HASHTAG
# ==========================================
with tab_hashtag:
    st.subheader("🏷️ Scrape Postingan Berdasarkan Hashtag")

    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        hashtag_input = st.text_input("Masukkan Hashtag (contoh: indonesia atau #photography)", placeholder="hashtag")
    with h_col2:
        st.write("")
        st.write("")
        btn_scrape_hashtag = st.button("🚀 Mulai Scrape Hashtag", use_container_width=True, type="primary")

    if btn_scrape_hashtag and hashtag_input:
        with st.status("🏷️ Memproses Scraping Hashtag...", expanded=True) as h_status:
            clean_tag = hashtag_input.strip().lstrip('#')
            st.write(f"🔍 **Langkah 1/2:** Mencari postingan publik dengan hashtag **#{clean_tag}**...")
            h_progress = st.progress(0)
            h_text = st.empty()

            h_logs = []
            with st.expander("🖥️ Backend Hashtag Scraping Terminal Logs", expanded=True):
                h_log_box = st.empty()

            def h_log_handler(msg):
                h_logs.append(msg)
                h_log_box.code("\n".join(h_logs), language="text")

            try:
                def update_h_progress(current, total):
                    pct = int((current / total) * 100)
                    h_progress.progress(pct)
                    h_text.caption(f"⏳ Progress postingan: **{current} / {total}** ({pct}%)")

                h_posts = scraper.scrape_hashtag_posts(
                    hashtag_input,
                    max_posts=max_posts,
                    progress_callback=update_h_progress,
                    log_callback=h_log_handler
                )
                st.session_state["hashtag_posts"] = h_posts

                h_status.update(label=f"✅ Scraping Hashtag Selesai! {len(h_posts)} Postingan Terkumpul.", state="complete", expanded=False)
                st.toast("Scraping hashtag selesai!", icon="🎉")
            except Exception as e:
                h_status.update(label="❌ Gagal Melakukan Scraping Hashtag", state="error", expanded=True)
                st.error(f"⚠️ Terjadi Kesalahan: {str(e)}")

    if st.session_state["hashtag_posts"]:
        h_posts = st.session_state["hashtag_posts"]
        df_h_posts = pd.DataFrame(h_posts)

        st.markdown("---")
        st.subheader(f"📊 Hasil Scraping Hashtag ({len(h_posts)} Post)")

        h_exp1, h_exp2, h_exp3 = st.columns(3)
        with h_exp1:
            st.download_button(
                label="📄 Download CSV",
                data=exporter.export_to_csv(df_h_posts),
                file_name=f"instagram_hashtag_posts.csv",
                mime="text/csv",
                use_container_width=True
            )
        with h_exp2:
            st.download_button(
                label="🌐 Download JSON",
                data=exporter.export_to_json(df_h_posts),
                file_name=f"instagram_hashtag_posts.json",
                mime="application/json",
                use_container_width=True
            )
        with h_exp3:
            st.download_button(
                label="📊 Download Excel",
                data=exporter.export_to_excel(df_h_posts),
                file_name=f"instagram_hashtag_posts.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        st.dataframe(
            df_h_posts[['owner_username', 'shortcode', 'timestamp', 'media_type', 'likes_count', 'comments_count', 'caption', 'post_url']],
            use_container_width=True
        )
