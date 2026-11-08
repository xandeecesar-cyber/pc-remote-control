# 🖥️ PC Remote Control

App de celular (web) para **controlar a tela do seu próprio PC** à distância: ver a tela ao vivo, mover o mouse, clicar, arrastar, rolar e digitar — tudo pelo navegador do celular. O app é só uma página estática que você hospeda **de graça no GitHub Pages**; o PC roda um pequeno servidor em Python.

> É um "controle remoto" caseiro, no mesmo espírito de um VNC/TeamViewer, feito para a **sua própria máquina**. Não é ferramenta de invasão: o servidor só roda se **você** o iniciar no seu PC, e exige uma senha.

---

## Como funciona

```
  Celular (navegador)                         Seu PC
  ┌─────────────────┐    WebSocket (Wi-Fi)   ┌──────────────────────┐
  │  index.html     │ ─────────────────────► │  server.py           │
  │  (GitHub Pages) │   comandos mouse/tecla │  - captura a tela     │
  │                 │ ◄───────────────────── │  - executa os cliques │
  └─────────────────┘   imagens da tela      └──────────────────────┘
```

---

## Parte 1 — Rodar o servidor no PC

1. Instale o Python 3.9+ (em Windows marque **"Add Python to PATH"**).
2. Baixe esta pasta e, dentro dela, instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o servidor escolhendo uma senha:
   ```bash
   python server.py --token minhaSenha123
   ```
   Opções úteis:
   | Opção | Padrão | Para quê |
   |-------|--------|----------|
   | `--token` | (obrigatório) | senha de acesso |
   | `--port` | 8765 | porta |
   | `--fps` | 12 | quadros por segundo |
   | `--quality` | 50 | qualidade do JPEG (10–95) |
   | `--monitor` | 1 | qual monitor capturar |
   | `--max-width` | 1280 | reduz a largura enviada p/ economizar dados (0 = original) |

4. Descubra o **IP local** do PC:
   - Windows: `ipconfig` → "Endereço IPv4" (ex.: `192.168.0.10`)
   - Linux/Mac: `hostname -I` ou `ifconfig`

### Permissões
- **macOS:** a primeira vez pede autorização em *Ajustes → Privacidade e Segurança → Acessibilidade* (para controlar mouse/teclado) e *Gravação de Tela*.
- **Windows:** o Firewall vai perguntar — libere o acesso na **rede privada**.

---

## Parte 2 — Publicar o app no GitHub (grátis)

1. Crie um repositório no GitHub (ex.: `pc-remote-control`).
2. Suba o arquivo **`index.html`** (pode subir a pasta inteira).
3. No repositório: **Settings → Pages → Branch: `main` / `/root` → Save**.
4. Em ~1 min seu app fica no ar em:
   `https://SEU_USUARIO.github.io/pc-remote-control/`
5. Abra esse link no celular e, se quiser, "Adicionar à tela de início" para virar um ícone de app.

---

## Parte 3 — Conectar

No app, preencha:
- **Endereço:** `ws://IP_DO_PC:8765` (ex.: `ws://192.168.0.10:8765`)
- **Senha:** a mesma do `--token`

> ⚠️ **Mesma rede Wi-Fi:** por padrão o celular precisa estar na mesma rede do PC. Veja abaixo para uso pela internet.

### ⚠️ Página HTTPS × servidor `ws://` (importante)
O GitHub Pages serve em **HTTPS**, e o navegador bloqueia uma página HTTPS de abrir um WebSocket **inseguro** (`ws://`). Você tem 3 saídas:

- **A) Usar na mesma rede, abrindo o app por HTTP.** Em vez do GitHub, abra o `index.html` servido pelo próprio PC ou localmente — aí `ws://` é permitido. (Simples para uso em casa.)
- **B) Túnel seguro (recomendado p/ GitHub Pages e p/ usar fora de casa).** Rode um túnel que expõe o servidor com `wss://`:
  ```bash
  cloudflared tunnel --url tcp://localhost:8765
  ```
  Use o endereço `wss://...` que ele te der, no campo de conexão.
- **C) Rodar o servidor com TLS** (certificado próprio) e conectar via `wss://`.

---

## Recursos incluídos
- ✅ Streaming da tela ao vivo (FPS e qualidade ajustáveis no app)
- ✅ Mover mouse, clique esquerdo, **clique direito**, **duplo clique**
- ✅ **Arrastar** (segura e move)
- ✅ Modo **scroll** (rolar páginas)
- ✅ **Teclado**: digitar texto, Enter, setas, atalhos (Ctrl+C, Ctrl+V, Alt+Tab) e modificadores (Ctrl/Alt/Shift/Win)
- ✅ Seleção de **monitor** (multi-telas)
- ✅ Autenticação por **token**
- ✅ Tela cheia e lembra o último endereço

## Ideias para evoluir
- Enviar/receber a área de transferência (copiar/colar entre celular e PC)
- Áudio do PC via WebRTC
- Vários dispositivos ao mesmo tempo
- Gravar a sessão em vídeo

## Segurança — leia
- Use **token forte** e, para acesso pela internet, **sempre** `wss://` (túnel ou TLS). Nunca exponha a porta direto na internet sem senha e sem criptografia.
- O servidor dá **controle total** da sua máquina a quem tiver o token — trate-o como senha de administrador.
- Use apenas em máquinas **suas**.

## Licença
MIT — use e modifique à vontade.
