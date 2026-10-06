# Reels da Sua Vez – memória do projeto

Este repositório reúne os vídeos verticais (Reels/TikTok) dos jogos de tabuleiro da **Sua Vez**. Leia
tudo antes de começar um vídeo novo: aqui está o que funcionou, o que não funcionou e do que o dono gostou.

## A loja

- **Sua Vez – Locação de Jogos de Tabuleiro**, Mauá e ABC (SP). Site: https://suavez.acervodejogos.com.br/
  (o logo veio de lá: `*/assets/logo_suavez.png`). Instagram: **@suavez_bg**.
- Aluguel de **5 dias**, com reserva online e retirada em Mauá. CTA padrão: "aluga na Sua Vez, o link tá na bio".
- O dono fala português do Brasil, usa **o celular** para quase tudo e grava a narração ele mesmo.

## O que todo vídeo precisa ter

- Formato 1080x1920, com **duração entre 1:00 e 1:10**. Passar de 1 minuto é obrigatório porque é o que monetiza.
- **Gancho** forte nos primeiros 2 segundos: uma pergunta ou provocação, com o texto já na tela.
- Marca d'água com o **logo da Sua Vez** no canto superior direito o vídeo inteiro (menos na tela final).
- **Tela final** com o logo, a caixa do jogo, "ALUGUE O ...", jogadores/tempo, "5 dias de jogo",
  "RESERVE ONLINE · RETIRE EM MAUÁ E ABC" e "LINK NA BIO · @SUAVEZ_BG".
- **Chamada para comentar** antes do CTA, com uma pergunta divertida sobre o jogo ("Comenta aqui!").
- Explicar as regras **certas**, conferindo no manual. Para isso servem o kit de imprensa e o Board Game Arena (veja Fontes).
- Entregar duas versões: **com legenda** e **sem legenda**. Loudness final de **≈ -14 LUFS**.

## Fluxo de trabalho que funciona

1. Escolher um **conceito visual diferente dos vídeos anteriores** (veja "Preferências"). Para decisões visuais,
   mande **imagens de comparação** com 2 ou 3 opções lado a lado. Funcionou muito bem para escolher o visual do Arquitetos.
2. Escrever o **roteiro em 9 falas curtas**, uma por cena, num total de ~55 s de fala. Mandar o roteiro no chat.
3. Fazer a **prévia** sem voz (trilha + legendas do roteiro) e mandar a versão 720p (`-b:v 2800k`) pelo chat.
4. Mandar o **link da página de gravação** sem o dono precisar pedir. Ele sempre pede ("lembra de me passar a narração").
5. O dono manda **9 arquivos .webm**, normalmente na ordem das falas. Ele **muda palavras** quando grava:
   o vídeo e as legendas seguem o que ele **falou**, não o roteiro.
6. Tratar, transcrever, encaixar (`narracao.py` → `narracao/timeline.json`), renderizar as duas versões e
   ajustar o volume. Depois conferir alguns quadros antes de mandar.

### Página de gravação (o que funcionou)

- Modelo: `voodoo-reels/gravador/Gravar_narracao_Vudu.html`, baseado no HTML que o próprio dono mandou. Cada fala tem
  o botão Gravar/Parar, o player e um medidor. No fim, "Baixar / enviar todas" usa `navigator.share` no celular. Os arquivos
  se chamam `<jogo>_narracao_NN`.
- Hospedar pelo **raw.githack.com com o hash do commit**, para ter HTTPS e o celular liberar o microfone. Exemplo:
  `https://raw.githack.com/erik-magalhaes/GitJoy/<commit>/architects-reels/gravador/Gravar_narracao_Arquitetos.html`.
  Antes de mandar o link, confira que ele responde 200.
- **Não funcionou:** gravar dentro de um Artifact (o microfone fica bloqueado), abrir o HTML local no navegador
  (não pede permissão do microfone) e gravar por cima do vídeo (ele quer gravar separado e que eu encaixe).

### Tratamento da voz (receita que deu certo)

- ffmpeg: `highpass=f=80, afftdn=nr=12:nf=-45:tn=1, equalizer 250 Hz -2.5 dB, 3200 Hz +3 dB, 9000 Hz (shelf) +1.5 dB,
  deesser=i=0.35, acompressor=threshold=-20dB:ratio=3:attack=6:release=140:makeup=3dB, loudnorm=I=-16:TP=-1.5:LRA=6`.
- Corte de silêncio por energia em numpy e reamostragem para **44,1 kHz** (a trilha usa SR=44100). Veja
  `mlem-reels/tratar_narracao.py`, que gera `frase_NN.wav` e `palavras.json` com faster-whisper `small`, int8, pt e tempos por palavra.
- `narracao.py` monta a linha do tempo: cada cena estica ou encolhe para caber a fala (LEAD 0,3 / GAP 0,45 / TAIL 0,6,
  CTA_HOLD 3,6 s e cena com no mínimo 70% da duração original). As legendas seguem os tempos reais das palavras.
- A trilha abaixa sozinha (ducking) quando há voz. Depois do render, suba ~**+1,6 dB** com `alimiter` para chegar a ≈ -14 LUFS.
- **Revise a transcrição:** o Whisper erra nomes e piadas. Já confundiu "Ô, Luisa Mell!" com "O Luís Améu",
  "MLEM" com "Milam" e "o capitão rola os dados" com "Capitão Rallos Dados". Corrija o `TEXTO` no `narracao.py`.

## Os vídeos feitos até agora

| Pasta | Jogo | Visual | Resultado |
|---|---|---|---|
| `voodoo-reels/` | Vudú | **Stop motion** de fotos reais recortadas, 12 poses/s com tremidinho, mesa escura e textos em adesivo branco (LuckiestGuy) | Aprovado, 1:06 |
| `sintonia-reels/` | Sintonia | **Motion graphics vetorial**, com os balões "CLARO!" na hora da discussão | Aprovado, 1:03 |
| `mlem-reels/` (`gibi.py`) | MLEM: Agência Espacial | **Gibi**: página de quadrinhos em que a câmera dá zoom num quadro por vez e o foguete atravessa os quadros com fumaça | Aprovado, 1:06 |
| `architects-reels/` (`stopmo.py`) | 7 Wonders Arquitetos | **Stop motion** com as peças oficiais sobre **papel quadriculado** (tema "prancheta"), com textos em fita crepe escritos à mão | Prévia aprovada; falta a narração |

Comandos comuns: `python3 <script>.py --frame T [T2 ...]` (quadros de teste em `out/frames.jpg`), `--only preview`
e sem argumentos (gera com e sem legenda). Os vídeos ficam em `out/`, que **não vai pro git**.

## Preferências do dono (gostou / não gostou)

- **Cada vídeo precisa ter uma cara própria.** No 7 Wonders ele gostou do stop motion, mas pediu para "afastar do Vudú".
  A solução foi manter a animação e trocar a mesa, a luz e o estilo dos textos.
- Gosta de stop motion **limpo**: peças retas e bem recortadas, sombra suave e o tremidinho da mão. Se o recorte ficar ruim, o vídeo todo fica ruim.
- Gosta de **detalhe e ação na tela**: dados rolando de verdade, peça saindo de um quadro para outro, fumaça, som em
  cada ação e a peça virando como no jogo de verdade (a maravilha passando de "em obras" para "construída").
- O roteiro precisa ser **claro**, na ordem de uma jogada real, e o CTA precisa ser forte. Ele já reclamou de roteiro confuso e de CTA fraco.
- **Nunca deixar texto cortado:** nada fora da tela, atrás da legenda (y > ~1590) ou atrás do logo.
  No gibi, o zoom cortava palavras e foi resolvido com `auto_cam` (enquadra o quadro inteiro mais os balões, numa área segura).
- A ação na tela tem que bater com a regra. No MLEM, o gato que "desce cedo" precisa pular **no começo** da trilha,
  e não no fim.
- **Não gostou de:**
  - massinha/claymation (no Vudú ele queria as peças reais, não massinha);
  - arte vetorial genérica para o MLEM;
  - recorte de fotos de celular em perspectiva (cartas "tortas/diagonais");
  - gatos e dados recortados à mão de foto;
  - stop motion tremido demais;
  - a planta azul (blueprint) com fotos tortas presas na folha.

## Fontes de imagem (do melhor para o pior)

1. **Kit de imprensa da editora.** No 7 Wonders foi o que salvou: https://www.rprod.com/en/press/<jogo>. O zip "BR"
   traz cartas retas em alta resolução, os tabuleiros de peças com transparência (os dois lados), caixa 3D, logo e o
   manual em PDF. `architects-reels/pecas_oficiais.py` mostra como extrair tudo, inclusive renderizar fichas vetoriais do
   PDF com PyMuPDF (`pip install pymupdf`). Imagens rasterizadas pequenas do PDF ficam pixeladas; prefira as vetoriais.
2. Fotos de produto de lojas brasileiras. Bravo Jogos (CDN simplo7, imagens 2000 px) e Two Head Games funcionaram com `curl -A Mozilla/5.0`.
   Fotos de peças em **fundo preto** recortam bem por limiar; já as fotos de celular em cima da mesa recortam mal.
3. BoardGameGeek e Ludopedia respondem 403 e a loja da Galápagos responde 401 pelo proxy. Não dá para depender deles.
4. Para conferir regras: a página de ajuda do jogo no Board Game Arena (en.doc.boardgamearena.com) e o manual do kit.

## Dicas técnicas (pegadinhas já resolvidas)

- Render: PIL/numpy gera os quadros e manda para o ffmpeg (`imageio_ffmpeg`), com `Pool(4)`. Um vídeo de 66 s a 30 fps leva ~10 min
  (o stop motion a 12 fps é bem mais rápido). Rode renders longos **em segundo plano** (`run_in_background`), sem `&`
  dentro do comando, porque o processo morre ou o log se perde.
- Pillow 12: bbox de texto vem em float, então arredonde com floor/ceil. `Image.resize(box=...)` não aceita caixa fora da
  imagem (deu erro no tremor da cena de guerra), então limite a caixa à imagem.
- Cuidado com `pkill`, que já matou o próprio shell. O `rm` combinado com `cd` é bloqueado, então use caminhos absolutos.
- Recortes: casco convexo resolve peças convexas (fichas e marcadores). Para fundo branco, use flood fill a partir das bordas;
  para fundo preto, use limiar com o maior componente. Peças de tabuleiro com transparência oficial são sempre melhores.
- Peças de dois lados (maravilha do 7 Wonders): o lado "construído" é o **verso**, então fica espelhado. A coluna da esquerda
  em obras vira a da direita construída (veja `VERSO` em `stopmo.py`).
- Estilos de texto prontos: adesivo de papel (`stopmo.sticker`, visual do Vudú), fita crepe, placa de pedra e tira
  de papel colorido (`architects-reels/temas.py`), além dos balões, caixas de narração e onomatopeias de gibi (`mlem-reels/gibi.py`).
- Trilha sintetizada em numpy (`voodoo-reels/audio.py`, `sintonia-reels/trilha.py`, `mlem-reels/som.py`,
  `architects-reels/trilha_arq.py`), com efeitos sincronizados por `cues` e `warp()` que acompanha o tempo da narração.

## Pendências

- **7 Wonders Arquitetos:** esperando os 9 áudios (`arq_narracao_01..09`). Gravador:
  `https://raw.githack.com/erik-magalhaes/GitJoy/6a9efbbc00e888124e30d4c5bd710ad1c6dd2bf6/architects-reels/gravador/Gravar_narracao_Arquitetos.html`.
  Ao receber: copie os áudios para `architects-reels/narracao/raw/`, trate (`tratar_narracao.py`), revise o `TEXTO` em
  `narracao.py`, rode `python3 narracao.py` e depois `python3 stopmo.py`, suba o volume e mande as duas versões.
  O kit de imprensa não está no repositório. Se precisar das peças de novo, baixe o zip BR e rode `pecas_oficiais.py <pasta>`.
- `architects-reels/arq.py` (planta azul) e `mlem-reels/mlem.py`/`stopmo.py` são versões **rejeitadas**. Ficam só como referência.
