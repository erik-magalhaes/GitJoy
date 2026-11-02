#!/bin/bash
# Gera as 3 versões: homem (voz normal), mulher e só texto. Saída: out/VOID_<versao>.mp4
cd "$(dirname "$0")"
set -e
for v in homem mulher texto; do
  case $v in
    homem) export VOZ_DIR=voz_h SEM_VOZ=0 ;;
    mulher) export VOZ_DIR=voz_m SEM_VOZ=0 ;;
    texto) export VOZ_DIR=voz SEM_VOZ=1 ;;
  esac
  export VERSAO=$v SAIDA_AUDIO=audio_$v.wav
  /usr/bin/python3 som_void.py
  /usr/bin/python3 real.py
  /usr/bin/python3 finaliza.py --audio out/audio_$v.wav void_$v
  echo "pronto $v"
done
