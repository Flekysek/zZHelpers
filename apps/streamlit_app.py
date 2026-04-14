from __future__ import annotations

import io
import os

import streamlit as st

from zzhelpers.base64_tools import decode_base64_text
from zzhelpers.image_tools import compress_or_resize, reformat
from zzhelpers.io import fmt_bytes, safe_filename
from zzhelpers.pfx_tools import extract_pfx, make_self_signed_pfx, wrap_to_pfx


st.set_page_config(page_title="zZHelpers", layout="centered")

with st.sidebar:
    try:
        st.image("LogoZz.jpg", use_container_width=True)
    except Exception:
        pass


def _section_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)


def page_convert() -> None:
    _section_header("Convert", "Převod Base64 řetězce na soubor (PDF/PNG/JPG/JPEG).")

    t_pdf, t_png, t_jpg, t_jpeg = st.tabs(["PDF", "PNG", "JPG", "JPEG"])
    out = "pdf"
    with t_pdf:
        out = "pdf"
    with t_png:
        out = "png"
    with t_jpg:
        out = "jpg"
    with t_jpeg:
        out = "jpeg"

    b64 = st.text_area("Base64 řetězec", height=180, placeholder="Vlož base64 řetězec nebo data URL…")

    col1, col2 = st.columns([1, 1])
    with col1:
        filename = st.text_input("Název souboru (bez přípony)", value="zZToolExport")
    with col2:
        mime_map = {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
        }
        mime = mime_map[out]

    if st.button("Připravit ke stažení", type="primary", use_container_width=True):
        try:
            res = decode_base64_text(b64)
            fname = safe_filename(filename, default="zZToolExport")
            st.success(f"Dekódováno: {fmt_bytes(len(res.data))}")
            st.download_button(
                "Stáhnout",
                data=res.data,
                file_name=f"{fname}.{out}",
                mime=mime,
                use_container_width=True,
            )
        except Exception as e:
            st.error(str(e) or "Chyba při dekódování base64.")


def page_compress() -> None:
    _section_header("Compress", "Komprese a konverze obrázků (PNG/JPG).")

    img = st.file_uploader("Nahraj obrázek", type=["png", "jpg", "jpeg"])
    if not img:
        return

    base = os.path.splitext(img.name)[0]
    st.image(img.getvalue(), caption=f"Originál ({img.name}, {fmt_bytes(img.size)})", use_container_width=True)

    mode = st.radio("Režim", ["Komprese", "Změna formátu"], horizontal=True, index=0)

    if mode == "Komprese":
        out_fmt_ui = st.radio("Výstupní formát", ["PNG", "JPG / JPEG"], horizontal=True, index=1)
        out_fmt = "PNG" if out_fmt_ui == "PNG" else "JPEG"

        scale = st.slider("Zmenšení rozlišení (%)", min_value=5, max_value=100, value=100, step=1)
        quality = 85
        if out_fmt == "JPEG":
            quality = st.slider("Kvalita JPG (%)", min_value=1, max_value=100, value=85, step=1)

        if st.button("Vygenerovat", type="primary", use_container_width=True):
            try:
                res = compress_or_resize(
                    image_bytes=img.getvalue(),
                    out_format=out_fmt,
                    scale_percent=scale,
                    jpeg_quality=quality,
                    filename_base=safe_filename(base, default="image"),
                )
                st.image(res.data, caption=f"Výsledek ({res.width}×{res.height}, {fmt_bytes(len(res.data))})", use_container_width=True)
                st.download_button(
                    "Stáhnout výsledek",
                    data=io.BytesIO(res.data),
                    file_name=res.filename,
                    mime=res.mime,
                    use_container_width=True,
                )
            except Exception as e:
                st.error(str(e) or "Chyba při zpracování obrázku.")
    else:
        out_fmt_ui = st.radio("Převést do formátu", ["PNG", "JPG / JPEG"], horizontal=True, index=0)
        out_fmt = "PNG" if out_fmt_ui == "PNG" else "JPEG"

        quality = 92
        if out_fmt == "JPEG":
            quality = st.slider("Kvalita JPG (%)", min_value=1, max_value=100, value=92, step=1)

        if st.button("Převést", type="primary", use_container_width=True):
            try:
                res = reformat(
                    image_bytes=img.getvalue(),
                    out_format=out_fmt,
                    jpeg_quality=quality,
                    filename_base=safe_filename(base, default="image"),
                )
                st.image(res.data, caption=f"Výsledek ({res.width}×{res.height}, {fmt_bytes(len(res.data))})", use_container_width=True)
                st.download_button(
                    "Stáhnout převedený obrázek",
                    data=io.BytesIO(res.data),
                    file_name=res.filename.replace("_out.", "."),
                    mime=res.mime,
                    use_container_width=True,
                )
            except Exception as e:
                st.error(str(e) or "Chyba při převodu.")


def page_pfx() -> None:
    _section_header("Create", "Generování a extrakce PFX souborů (lokálně).")

    tab_make, tab_wrap, tab_extract = st.tabs(["✦ Vytvořit PFX", "⧉ Zabalit do PFX", "⊡ Rozbalit PFX"])

    with tab_make:
        st.subheader("Self-signed PFX")
        col1, col2 = st.columns(2)
        with col1:
            cn = st.text_input("Common Name (CN) *", placeholder="mujserver.cz")
            o = st.text_input("Organization (O)", placeholder="Moje Firma s.r.o.")
            ou = st.text_input("Organizational Unit (OU)", placeholder="IT")
        with col2:
            l = st.text_input("Locality (L)", placeholder="Praha")
            st_ = st.text_input("State (ST)", placeholder="Hlavní město Praha")
            c = st.text_input("Country (C)", placeholder="CZ", max_chars=2)

        col3, col4 = st.columns(2)
        with col3:
            bits = st.selectbox("Délka klíče RSA", [2048, 4096], index=0)
            days = st.number_input("Platnost (dny)", min_value=1, max_value=9999, value=365, step=1)
        with col4:
            p1 = st.text_input("Heslo PFX *", type="password")
            p2 = st.text_input("Potvrdit heslo *", type="password")

        if st.button("Vygenerovat .pfx", type="primary", use_container_width=True, key="make_pfx"):
            try:
                res = make_self_signed_pfx(
                    common_name=cn,
                    organization=o,
                    organizational_unit=ou,
                    locality=l,
                    state=st_,
                    country=c,
                    rsa_bits=int(bits),
                    days_valid=int(days),
                    pfx_password=p1,
                    pfx_password2=p2,
                )
                st.success("Hotovo.")
                st.download_button(
                    f"Stáhnout {res.filename}",
                    data=io.BytesIO(res.pfx_bytes),
                    file_name=res.filename,
                    mime="application/x-pkcs12",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(str(e) or "Chyba při generování PFX.")

    with tab_wrap:
        st.subheader("Cert + key (+ chain) → PFX")
        cert_file = st.file_uploader("Certifikát (PEM/DER) *", type=["pem", "crt", "cer", "der"], key="wrap_cert")
        key_file = st.file_uploader("Privátní klíč (PEM) *", type=["key", "pem"], key="wrap_key")
        chain_file = st.file_uploader("CA řetězec (PEM, volitelné)", type=["pem", "crt", "cer"], key="wrap_chain")

        col1, col2 = st.columns(2)
        with col1:
            pfx_password = st.text_input("Heslo PFX *", type="password", key="wrap_p1")
        with col2:
            pfx_password2 = st.text_input("Potvrdit heslo PFX *", type="password", key="wrap_p2")

        key_password = st.text_input("Heslo privátního klíče (pokud je šifrovaný)", type="password", key="wrap_kp")
        friendly_name = st.text_input("Friendly name (volitelné)", key="wrap_fn")

        if st.button("Zabalit do .pfx", type="primary", use_container_width=True, key="wrap_btn"):
            try:
                if not cert_file:
                    raise ValueError("Nejprve nahraj certifikát.")
                if not key_file:
                    raise ValueError("Nejprve nahraj privátní klíč.")

                res = wrap_to_pfx(
                    cert_bytes=cert_file.getvalue(),
                    key_bytes=key_file.getvalue(),
                    chain_bytes=chain_file.getvalue() if chain_file else b"",
                    pfx_password=pfx_password,
                    pfx_password2=pfx_password2,
                    key_password=key_password or None,
                    friendly_name=(friendly_name.strip() or None),
                )
                st.success("Hotovo.")
                st.download_button(
                    f"Stáhnout {res.filename}",
                    data=io.BytesIO(res.pfx_bytes),
                    file_name=res.filename,
                    mime="application/x-pkcs12",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(str(e) or "Chyba při balení.")

    with tab_extract:
        st.subheader("PFX → PEM")
        pfx_file = st.file_uploader("Nahraj .pfx / .p12", type=["pfx", "p12"], key="ext_pfx")
        pfx_pass = st.text_input("Heslo souboru (pokud má)", type="password", key="ext_pass")

        if st.button("Rozbalit", type="primary", use_container_width=True, key="ext_btn"):
            try:
                if not pfx_file:
                    raise ValueError("Nejprve nahraj .pfx soubor.")

                res = extract_pfx(pfx_bytes=pfx_file.getvalue(), pfx_password=pfx_pass or None)
                st.success("Hotovo.")

                st.text_area("Certifikát (PEM)", value=res.cert_pem, height=200)
                st.download_button(
                    "Stáhnout certifikat.pem",
                    data=res.cert_pem.encode("utf-8"),
                    file_name="certifikat.pem",
                    mime="application/x-pem-file",
                    use_container_width=True,
                )

                if res.key_pem:
                    st.text_area("Privátní klíč (PEM)", value=res.key_pem, height=200)
                    st.download_button(
                        "Stáhnout privatni-klic.key",
                        data=res.key_pem.encode("utf-8"),
                        file_name="privatni-klic.key",
                        mime="application/x-pem-file",
                        use_container_width=True,
                    )

                if res.chain_pem:
                    st.text_area("CA řetězec (PEM)", value=res.chain_pem, height=200)
                    st.download_button(
                        "Stáhnout chain.pem",
                        data=res.chain_pem.encode("utf-8"),
                        file_name="chain.pem",
                        mime="application/x-pem-file",
                        use_container_width=True,
                    )
            except Exception as e:
                st.error(str(e) or "Chyba při rozbalování.")


pages = {
    "Convert": page_convert,
    "Compress": page_compress,
    "Create": page_pfx,
}

choice = st.sidebar.radio("zZHelpers", list(pages.keys()))
pages[choice]()

