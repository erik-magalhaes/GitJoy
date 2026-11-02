#!/bin/bash
cd "$(dirname "$0")"
set -e
export VERSAO=texto VOZ_DIR=voz SEM_VOZ=1 SAIDA_AUDIO=audio_texto.wav
/usr/bin/python3 som_void.py
/usr/bin/python3 real.py
/usr/bin/python3 finaliza.py --audio out/audio_texto.wav void_texto
