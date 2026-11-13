import io
import json
import zipfile
import pandas as pd
from typing import Union, Any

def prepare_dataframe(data: Union[list, pd.DataFrame]) -> pd.DataFrame:
    """
    Mengonversi data list of dict ke Pandas DataFrame dan merapikan kolom untuk ekspor.
    """
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        df = pd.DataFrame(data)

    if df.empty:
        return df

    # Hapus atau ubah kolom kompleks seperti list dict media_urls menjadi string ringkas jika ada
    if "media_urls" in df.columns:
        df["media_urls"] = df["media_urls"].apply(
            lambda urls: ", ".join([u["url"] for u in urls if isinstance(u, dict) and "url" in u]) if isinstance(urls, list) else str(urls)
        )
    return df

def export_to_csv(data: Union[list, pd.DataFrame]) -> bytes:
    """
    Ekspor data ke format CSV.
    """
    df = prepare_dataframe(data)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
    return csv_buffer.getvalue().encode('utf-8-sig')

def export_to_json(data: Union[list, pd.DataFrame]) -> bytes:
    """
    Ekspor data ke format JSON (formatted).
    """
    if isinstance(data, pd.DataFrame):
        records = data.to_dict(orient='records')
    else:
        records = data

    json_str = json.dumps(records, indent=4, ensure_ascii=False)
    return json_str.encode('utf-8')

def export_to_excel(data: Union[list, pd.DataFrame]) -> bytes:
    """
    Ekspor data ke format Excel (.xlsx).
    """
    df = prepare_dataframe(data)
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Instagram Data')
    return excel_buffer.getvalue()

def create_media_zip(media_items: list, download_func, progress_callback=None, log_callback=None) -> bytes:
    """
    Menggabungkan file media (foto/video) ke dalam file ZIP di memori.
    media_items: list dict dengan struktur {"filename": str, "url": str}
    download_func: fungsi callback untuk mengunduh bytes dari URL
    progress_callback: fungsi callback (current, total, filename)
    """
    zip_buffer = io.BytesIO()
    total = len(media_items)
    with zipfile.ZipFile(zip_buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for idx, item in enumerate(media_items):
            url = item.get("url")
            filename = item.get("filename", f"media_{idx+1}.jpg")
            if progress_callback:
                progress_callback(idx + 1, total, filename)
            if not url:
                continue
            try:
                content = download_func(url, log_callback=log_callback) if log_callback else download_func(url)
                zf.writestr(filename, content)
            except Exception as e:
                zf.writestr(f"error_{filename}.txt", f"Gagal mengunduh {url}: {str(e)}")
    return zip_buffer.getvalue()
