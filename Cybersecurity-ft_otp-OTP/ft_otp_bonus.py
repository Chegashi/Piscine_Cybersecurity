#!/usr/bin/env python3

from __future__ import annotations

import secrets
import time
import tkinter as tk
from urllib.parse import quote, urlencode
from tkinter import filedialog, messagebox, ttk

import qrcode
from PIL import ImageTk

from ft_otp_core import (
    KEY_FILE,
    TIME_STEP_SECONDS,
    OtpError,
    base32_secret,
    load_encrypted_key,
    load_plain_hex_key,
    save_encrypted_key,
    totp,
)


WINDOW_PAD = {"padx": 10, "pady": 5}
ISSUER = "ft_otp"
ACCOUNT_NAME = "ft_otp"


class FtOtpApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ft_otp")
        self.resizable(False, False)
        self._key_bytes: bytes | None = None
        self._qr_photo = None
        self._build_ui()
        self._tick()

    def _build_ui(self) -> None:
        frm_seed = ttk.LabelFrame(self, text=" Key Generation (-g) ")
        frm_seed.grid(row=0, column=0, columnspan=2, sticky="ew", **WINDOW_PAD)

        ttk.Label(frm_seed, text="Hex key file:").grid(
            row=0,
            column=0,
            sticky="w",
            **WINDOW_PAD,
        )
        self._seed_path = tk.StringVar()
        ttk.Entry(frm_seed, textvariable=self._seed_path, width=38).grid(
            row=0,
            column=1,
            **WINDOW_PAD,
        )
        ttk.Button(frm_seed, text="Browse", command=self._browse_seed).grid(
            row=0,
            column=2,
            **WINDOW_PAD,
        )
        ttk.Button(frm_seed, text="Generate random seed", command=self._gen_random_seed).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            **WINDOW_PAD,
        )
        ttk.Button(frm_seed, text=f"Save to {KEY_FILE}", command=self._save_key).grid(
            row=1,
            column=2,
            **WINDOW_PAD,
        )

        frm_load = ttk.LabelFrame(self, text=" Load Key (-k) ")
        frm_load.grid(row=1, column=0, columnspan=2, sticky="ew", **WINDOW_PAD)

        ttk.Label(frm_load, text="Key file:").grid(row=0, column=0, sticky="w", **WINDOW_PAD)
        self._key_path = tk.StringVar(value=str(KEY_FILE))
        ttk.Entry(frm_load, textvariable=self._key_path, width=38).grid(
            row=0,
            column=1,
            **WINDOW_PAD,
        )
        ttk.Button(frm_load, text="Browse", command=self._browse_key).grid(
            row=0,
            column=2,
            **WINDOW_PAD,
        )
        ttk.Button(frm_load, text="Load key", command=self._load_key).grid(
            row=1,
            column=0,
            **WINDOW_PAD,
        )

        frm_otp = ttk.LabelFrame(self, text=" One-Time Password ")
        frm_otp.grid(row=2, column=0, sticky="nsew", **WINDOW_PAD)

        self._otp_var = tk.StringVar(value="------")
        ttk.Label(
            frm_otp,
            textvariable=self._otp_var,
            font=("Courier", 40, "bold"),
        ).grid(row=0, column=0, padx=20, pady=10)

        self._countdown_var = tk.StringVar(value="load a key to start")
        ttk.Label(frm_otp, textvariable=self._countdown_var, font=("Courier", 11)).grid(
            row=1,
            column=0,
        )

        self._progress = ttk.Progressbar(frm_otp, length=220, maximum=30, mode="determinate")
        self._progress.grid(row=2, column=0, padx=10, pady=8)

        frm_qr = ttk.LabelFrame(self, text=" QR Code (scan with authenticator) ")
        frm_qr.grid(row=2, column=1, sticky="nsew", **WINDOW_PAD)

        self._qr_label = ttk.Label(frm_qr, text="Load a key\nto show QR", anchor="center")
        self._qr_label.grid(row=0, column=0, padx=20, pady=20)

        self._status = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self._status, relief="sunken", anchor="w").grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 6)
        )

    def _browse_seed(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Hex files", "*.hex"), ("All files", "*")])
        if path:
            self._seed_path.set(path)

    def _browse_key(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Key files", "*.key"), ("All files", "*")])
        if path:
            self._key_path.set(path)

    def _gen_random_seed(self) -> None:
        hex_key = secrets.token_hex(32)
        path = filedialog.asksaveasfilename(
            defaultextension=".hex",
            initialfile="key.hex",
            filetypes=[("Hex files", "*.hex")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="ascii") as seed_file:
                seed_file.write(hex_key)
            self._seed_path.set(path)
            self._status.set(f"Random seed saved to {path}")
        except OSError as exc:
            self._show_error(exc)

    def _save_key(self) -> None:
        path = self._seed_path.get().strip()
        if not path:
            messagebox.showerror("Error", "Select a hex key file first.")
            return
        try:
            hex_key = load_plain_hex_key(path)
            save_encrypted_key(hex_key, KEY_FILE)
            self._activate(bytes.fromhex(hex_key))
            self._status.set(f"Key encrypted and saved to {KEY_FILE}")
        except OtpError as exc:
            self._show_error(exc)

    def _load_key(self) -> None:
        path = self._key_path.get().strip()
        try:
            self._activate(load_encrypted_key(path))
            self._status.set(f"Key loaded from {path}")
        except OtpError as exc:
            self._show_error(exc)

    def _activate(self, key_bytes: bytes) -> None:
        self._key_bytes = key_bytes
        uri = self._otp_uri(key_bytes)
        img = qrcode.make(uri).resize((200, 200))
        self._qr_photo = ImageTk.PhotoImage(img)
        self._qr_label.config(image=self._qr_photo, text="")

    def _otp_uri(self, key_bytes: bytes) -> str:
        label = quote(f"{ISSUER}:{ACCOUNT_NAME}", safe="")
        query = urlencode({"secret": base32_secret(key_bytes), "issuer": ISSUER})
        return f"otpauth://totp/{label}?{query}"

    def _show_error(self, error: Exception) -> None:
        messagebox.showerror("Error", str(error))
        self._status.set("Error")

    def _tick(self) -> None:
        if self._key_bytes:
            remaining = TIME_STEP_SECONDS - (int(time.time()) % TIME_STEP_SECONDS)
            self._otp_var.set(totp(self._key_bytes))
            self._countdown_var.set(f"refreshes in {remaining}s")
            self._progress["value"] = remaining
        self.after(1000, self._tick)


if __name__ == "__main__":
    FtOtpApp().mainloop()
