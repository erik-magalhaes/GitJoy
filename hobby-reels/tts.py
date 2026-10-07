"""Gera uma fala com voz neural (edge-tts) pelo proxy: tts.py VOZ "texto" saida.mp3 [rate] [pitch]"""
import asyncio, ssl, os, sys
import edge_tts.communicate as c
c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
async def main():
    rate = sys.argv[4] if len(sys.argv) > 4 else "+0%"
    pitch = sys.argv[5] if len(sys.argv) > 5 else "+0Hz"
    com = c.Communicate(sys.argv[2], sys.argv[1], rate=rate, pitch=pitch, proxy=os.environ.get("HTTPS_PROXY"))
    await com.save(sys.argv[3])
asyncio.run(main())
