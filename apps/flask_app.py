from __future__ import annotations

import os

from flask import Flask, Response, request, send_from_directory

from zzhelpers.pfx_tools import wrap_to_pfx


APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(__name__, static_folder=None)


@app.get("/api/health")
def health() -> Response:
    return Response("ok", mimetype="text/plain; charset=utf-8", headers={"Cache-Control": "no-store"})


@app.get("/")
def index() -> Response:
    return send_from_directory(APP_ROOT, "index.html")


@app.get("/controller.js")
def controller_js() -> Response:
    return send_from_directory(APP_ROOT, "controller.js")


@app.get("/LogoZz.jpg")
def logo() -> Response:
    return send_from_directory(APP_ROOT, "LogoZz.jpg")


@app.post("/api/wrap-pfx")
def api_wrap_pfx() -> Response:
    try:
        cert_f = request.files.get("cert")
        key_f = request.files.get("key")
        chain_f = request.files.get("chain")

        if not cert_f or not cert_f.readable():
            raise ValueError("Chybí soubor: cert")
        if not key_f or not key_f.readable():
            raise ValueError("Chybí soubor: key")

        cert_bytes = cert_f.read()
        key_bytes = key_f.read()
        chain_bytes = chain_f.read() if chain_f else b""

        pfx_password = (request.form.get("pfxPassword") or "").strip()
        pfx_password2 = (request.form.get("pfxPassword2") or "").strip()
        key_password = (request.form.get("keyPassword") or "").strip() or None
        friendly_name = (request.form.get("friendlyName") or "").strip() or None

        res = wrap_to_pfx(
            cert_bytes=cert_bytes,
            key_bytes=key_bytes,
            chain_bytes=chain_bytes,
            pfx_password=pfx_password,
            pfx_password2=pfx_password2,
            key_password=key_password,
            friendly_name=friendly_name,
        )

        return Response(
            res.pfx_bytes,
            mimetype="application/x-pkcs12",
            headers={
                "Content-Disposition": f'attachment; filename="{res.filename}"',
                "Cache-Control": "no-store",
            },
        )
    except ValueError as e:
        return Response(str(e) or "Neplatné vstupy.", status=400, mimetype="text/plain; charset=utf-8")
    except TypeError:
        return Response(
            "Špatné heslo ke klíči nebo neplatný formát privátního klíče.",
            status=400,
            mimetype="text/plain; charset=utf-8",
        )
    except Exception:
        return Response(
            "Neočekávaná chyba při balení. Zkontroluj vstupy (cert/key/chain) a hesla.",
            status=500,
            mimetype="text/plain; charset=utf-8",
        )


def main() -> None:
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()

