# 📱 Gerar o APK (sem instalar nada no PC)

O app Android está na pasta `android/`. Ele já traz a interface de controle embutida — ao abrir, você só digita o endereço do PC e a senha. Como a interface roda localmente dentro do app, **não há bloqueio de `ws://`** (diferente da versão de site).

Você tem dois caminhos para obter o `.apk`:

---

## ✅ Caminho 1 — GitHub compila pra você (recomendado)

Não precisa de Android Studio. O GitHub monta o APK na nuvem.

1. Crie um repositório no GitHub e suba **esta pasta inteira** (incluindo `android/` e `.github/`).
2. Vá na aba **Actions** do repositório. O fluxo **"Build APK"** roda sozinho a cada envio (ou clique em **Run workflow** para rodar na hora).
3. Quando terminar (uns 2–4 min), abra a execução concluída e baixe o artefato **`PCRemote-apk`** (um `.zip` com o `app-debug.apk` dentro).
4. Passe o `app-debug.apk` para o celular e instale.

### Instalar o APK no celular
- Transfira o arquivo (cabo, Google Drive, Telegram pra você mesmo etc.).
- Abra o `.apk`. O Android vai pedir para permitir **"instalar de fontes desconhecidas"** — permita para o app que está abrindo (navegador/arquivos).
- Confirme a instalação. Pronto, o ícone **PC Remote** aparece na gaveta de apps.

> É um APK "debug" (não assinado para a Play Store), perfeito para uso pessoal. Para publicar na loja seria preciso assinar com uma chave de release — posso montar esse passo se quiser.

---

## 🛠️ Caminho 2 — Compilar você mesmo

Se tiver o **Android Studio** (ou o SDK + Java 17):

```bash
cd android
./gradlew assembleDebug        # Linux/Mac
gradlew.bat assembleDebug      # Windows
```

O APK sai em:
```
android/app/build/outputs/apk/debug/app-debug.apk
```

---

## Usando o app
1. No PC, deixe o servidor rodando (veja o `README.md` principal):
   ```bash
   python server.py --token minhaSenha123
   ```
2. Abra o app **PC Remote** no celular.
3. Digite `ws://IP_DO_PC:8765` e a senha. Conecte.

Mesma rede Wi-Fi para uso em casa; túnel `wss://` (cloudflared) para usar pela internet — detalhes no `README.md` principal.

## Estrutura
```
android/
├── settings.gradle, build.gradle, gradle.properties
├── gradlew, gradlew.bat, gradle/wrapper/      ← Gradle wrapper (já incluso)
└── app/
    ├── build.gradle
    └── src/main/
        ├── AndroidManifest.xml
        ├── assets/index.html                  ← a interface de controle
        ├── java/com/pcremote/control/MainActivity.java
        └── res/                               ← ícone, tema, textos
.github/workflows/build-apk.yml                ← compila o APK na nuvem
```
