from __future__ import annotations

import io

import streamlit as st

from pfx_wrap import wrap_to_pfx


st.set_page_config(page_title="ZzTools – PFX wrapper", layout="centered")
st.title("Zabalit cert+key → PFX")
st.caption("Vše běží lokálně. Soubory ani hesla se nikam neodesílají (Streamlit běží na tvém PC).")

cert_file = st.file_uploader("Certifikát (PEM/DER)", type=["pem", "crt", "cer", "der"])
key_file = st.file_uploader("Privátní klíč (PEM)", type=["key", "pem"])
chain_file = st.file_uploader("CA řetězec (PEM, volitelné)", type=["pem", "crt", "cer"])

col1, col2 = st.columns(2)
with col1:
    pfx_password = st.text_input("Heslo PFX", type="password")
with col2:
    pfx_password2 = st.text_input("Potvrdit heslo PFX", type="password")

key_password = st.text_input("Heslo privátního klíče (pokud je šifrovaný)", type="password")
friendly_name = st.text_input("Friendly name (volitelné)")

btn = st.button("Vygenerovat .pfx", type="primary", use_container_width=True)

if btn:
    try:
        if not cert_file:
            st.error("Nejprve nahraj certifikát.")
            st.stop()
        if not key_file:
            st.error("Nejprve nahraj privátní klíč.")
            st.stop()

        cert_bytes = cert_file.getvalue()
        key_bytes = key_file.getvalue()
        chain_bytes = chain_file.getvalue() if chain_file else b""

        result = wrap_to_pfx(
            cert_bytes=cert_bytes,
            key_bytes=key_bytes,
            chain_bytes=chain_bytes,
            pfx_password=pfx_password,
            pfx_password2=pfx_password2,
            key_password=key_password or None,
            friendly_name=(friendly_name.strip() or None),
        )

        st.success("Hotovo.")
        st.download_button(
            label=f"Stáhnout {result.filename}",
            data=io.BytesIO(result.pfx_bytes),
            file_name=result.filename,
            mime="application/x-pkcs12",
            use_container_width=True,
        )
    except Exception as e:
        st.error(str(e) or "Chyba při balení.")

