#!/usr/bin/env python3
"""
PC Remote Control - Servidor (roda no SEU PC)
=============================================
Captura a tela e aceita comandos de mouse/teclado vindos do celular.
Comunicação via WebSocket. Autenticação por token.

Uso:
    python server.py --token MINHA_SENHA --port 8765 --fps 12 --quality 50

Depois abra o app (index.html) no celular e conecte em:
    ws://IP_DO_SEU_PC:8765
"""
import argparse
import asyncio
import base64
import json
import time

try:
    import websockets
except ImportError:
    raise SystemExit("Faltando 'websockets'. Rode: pip install websockets")

try:
    import mss
except ImportError:
    raise SystemExit("Faltando 'mss'. Rode: pip install mss")

try:
    from PIL import Image
except ImportError:
    raise SystemExit("Faltando 'Pillow'. Rode: pip install Pillow")

try:
    from pynput.mouse import Controller as MouseController, Button
    from pynput.keyboard import Controller as KeyboardController, Key
except ImportError:
    raise SystemExit("Faltando 'pynput'. Rode: pip install pynput")

import io

mouse = MouseController()
keyboard = KeyboardController()

# Mapa de teclas especiais enviadas pelo cliente -> pynput
SPECIAL_KEYS = {
    "enter": Key.enter, "backspace": Key.backspace, "tab": Key.tab,
    "esc": Key.esc, "space": Key.space, "up": Key.up, "down": Key.down,
    "left": Key.left, "right": Key.right, "delete": Key.delete,
    "home": Key.home, "end": Key.end, "pageup": Key.page_up,
    "pagedown": Key.page_down, "ctrl": Key.ctrl, "alt": Key.alt,
    "shift": Key.shift, "cmd": Key.cmd, "win": Key.cmd,
    "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
    "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
    "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
}
BUTTONS = {"left": Button.left, "right": Button.right, "middle": Button.middle}


class ScreenSource:
    """Captura um monitor específico e devolve JPEG + dimensões."""
    def __init__(self, monitor_index, quality):
        self.sct = mss.mss()
        self.monitors = self.sct.monitors  # [0]=todos juntos, [1..]=cada um
        self.set_monitor(monitor_index)
        self.quality = quality

    def set_monitor(self, index):
        if index < 1 or index >= len(self.sct.monitors):
            index = 1
        self.monitor_index = index
        self.mon = self.sct.monitors[index]

    def grab_jpeg(self, max_width):
        shot = self.sct.grab(self.mon)
        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
        w, h = img.size
        if max_width and w > max_width:
            ratio = max_width / w
            img = img.resize((max_width, int(h * ratio)))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=self.quality)
        return buf.getvalue(), w, h


def apply_input(event, screen):
    """Executa um comando recebido do celular sobre a tela real."""
    t = event.get("t")
    mon = screen.mon
    ox, oy = mon["left"], mon["top"]
    sw, sh = mon["width"], mon["height"]

    # Coordenadas chegam normalizadas 0..1 em relação ao monitor
    def abs_pos(nx, ny):
        return ox + int(nx * sw), oy + int(ny * sh)

    if t == "move":
        mouse.position = abs_pos(event["x"], event["y"])
    elif t == "click":
        mouse.position = abs_pos(event["x"], event["y"])
        btn = BUTTONS.get(event.get("button", "left"), Button.left)
        mouse.click(btn, event.get("count", 1))
    elif t == "down":
        mouse.position = abs_pos(event["x"], event["y"])
        mouse.press(BUTTONS.get(event.get("button", "left"), Button.left))
    elif t == "up":
        mouse.release(BUTTONS.get(event.get("button", "left"), Button.left))
    elif t == "scroll":
        mouse.scroll(event.get("dx", 0), event.get("dy", 0))
    elif t == "type":
        keyboard.type(event.get("text", ""))
    elif t == "key":
        name = event.get("key", "").lower()
        k = SPECIAL_KEYS.get(name, name if len(name) == 1 else None)
        if k is None:
            return
        mods = event.get("mods", [])
        mkeys = [SPECIAL_KEYS[m] for m in mods if m in SPECIAL_KEYS]
        for m in mkeys:
            keyboard.press(m)
        keyboard.press(k)
        keyboard.release(k)
        for m in reversed(mkeys):
            keyboard.release(m)


async def handler(ws, token, screen, fps, max_width):
    authed = False
    delay = 1.0 / max(1, fps)

    async def sender():
        while True:
            if authed:
                data, rw, rh = screen.grab_jpeg(max_width)
                b64 = base64.b64encode(data).decode("ascii")
                await ws.send(json.dumps({
                    "t": "frame", "img": b64,
                    "rw": rw, "rh": rh, "mon": screen.monitor_index,
                    "mons": len(screen.sct.monitors) - 1,
                }))
            await asyncio.sleep(delay)

    send_task = None
    try:
        async for raw in ws:
            msg = json.loads(raw)
            if msg.get("t") == "auth":
                if msg.get("token") == token:
                    authed = True
                    await ws.send(json.dumps({"t": "ok"}))
                    send_task = asyncio.create_task(sender())
                else:
                    await ws.send(json.dumps({"t": "err", "m": "token invalido"}))
                    return
            elif not authed:
                continue
            elif msg.get("t") == "setmon":
                screen.set_monitor(int(msg.get("i", 1)))
            elif msg.get("t") == "quality":
                screen.quality = max(10, min(95, int(msg.get("v", 50))))
            else:
                apply_input(msg, screen)
    except websockets.ConnectionClosed:
        pass
    finally:
        if send_task:
            send_task.cancel()


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True, help="Senha de acesso")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--quality", type=int, default=50)
    ap.add_argument("--monitor", type=int, default=1)
    ap.add_argument("--max-width", type=int, default=1280,
                    help="Reduz a largura enviada p/ economizar banda (0 = original)")
    args = ap.parse_args()

    screen = ScreenSource(args.monitor, args.quality)
    print(f"Monitores detectados: {len(screen.sct.monitors) - 1}")
    print(f"Servidor ouvindo em ws://0.0.0.0:{args.port}  (token: {args.token})")
    print("No celular, conecte usando o IP local do PC, ex: ws://192.168.0.10:%d" % args.port)

    async with websockets.serve(
        lambda ws: handler(ws, args.token, screen, args.fps, args.max_width),
        args.host, args.port, max_size=2 ** 24,
    ):
        await asyncio.Future()  # roda para sempre


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEncerrado.")
