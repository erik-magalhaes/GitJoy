# Reels da Sua Vez – memória do projeto

Este repositório reúne os vídeos verticais (Reels/TikTok) dos jogos de tabuleiro da **Sua Vez**. Leia
tudo antes de começar um vídeo novo: aqui está o que funcionou, o que não funcionou e do que o dono gostou.

## Como continuar numa conversa nova (LEIA PRIMEIRO)

- Toda a memória do projeto está **neste arquivo** e no código da branch `claude/voodoo-stop-motion-video-rni4kj`
  (repositório erik-magalhaes/GitJoy). Numa sessão nova, use o mesmo repositório e a mesma branch: o Claude lê este
  arquivo sozinho. Brutos de vídeo e `out/` NÃO vão pro git; os brutos gravados estão no Drive dele
  (https://drive.google.com/drive/folders/1yGgKAxAUrJAipiu4p2687F4TaA8I6yCK, baixar com `python3 -m gdown`).
- Eu não consigo subir arquivos no Drive dele (só baixar de pasta pública). Entregar pelo chat; se ele conectar o
  Google Drive em claude.ai → Configurações → Conectores, dá para subir direto.
- **Estado em 10/out/2026:**
  - Entregues e aprovados: vídeo do Dia das Crianças v2 (`gravados-reels/criancas2.py`), cartão do evento 9x9
    (`promo/cartao_evento.py`), carrossel do feed "jogos modernos" (`hobby-reels/carrossel.py`, 8 telas 1080x1350;
    na tela 4 o Go Cuckoo foi trocado pelo Gravity porque ele achou a foto "amassada").
  - **Esperando narração dele:** Final Girl e 7 tipos de jogador
    (links nas seções abaixo).
  - **Esperando gravação dele:** vídeo da trend "5, 4, 3, 2, 1" de jogos de tabuleiro (roteiro mandado: 5 pra quem
    nunca jogou, 4 que destroem amizades, 3 pra dois, 2 que nunca cansa, 1 que todo mundo precisa jogar; ~30–45 s,
    números animados + capas oficiais + legenda) e o vídeo de Halloween (roteiro já mandado).
  - Microfone dele (Kaidi, lapela sem fio): redução de ruído que NÃO desliga, som "robótico"; recomendei gravar com o
    microfone do celular a 30–40 cm em cômodo silencioso.

## A loja

- **Sua Vez – Locação de Jogos de Tabuleiro**, Mauá e ABC (SP). Site: https://suavez.acervodejogos.com.br/
  (o logo veio de lá: `*/assets/logo_suavez.png`). Instagram: **@suavez_bg**.
- Aluguel de **5 dias**, com reserva online e **retirada em Mauá ou entrega em casa** (existe uma pequena taxa de entrega,
  mas ele pediu para **não citar a taxa** nas artes; o frete é combinado no checkout). Promoção de **prazo progressivo** (vale para todos os jogos do carrinho, pelo mesmo preço):
  **3 jogos = 7 dias, 5 jogos = 10 dias, 7 jogos = 15 dias** (arte em `promo/promo_progressivo.py`).
  CTA padrão: "aluga na Sua Vez, o link tá na bio". Não escreva só "retire em Mauá": cite também a entrega.
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
| `architects-reels/` (`stopmo.py`) | 7 Wonders Arquitetos | **Stop motion** com as peças oficiais sobre **papel quadriculado** (tema "prancheta"), com textos em fita crepe escritos à mão | **Narrado e entregue** (69,9 s, com e sem legenda) |
| `hobby-reels/` (`ludoteca.py`) | Institucional: o que são jogos modernos + preço loja × aluguel + prazo progressivo | **Estante da ludoteca** (opção 1): caixas do acervo em prateleiras de madeira, caixas saindo em stop motion, etiquetas kraft e de preço | **Narrado e entregue** (1:08, com e sem legenda) |
| `quiz-reels/` (`relampago.py`) | Quiz "Que jogo é esse?" (5 caixas do acervo) | **Zoom relâmpago** (opção 3 de `conceitos.py`): detalhe da arte em TELA CHEIA, anel de contagem 3 s, abre rápido para a caixa inteira sobre a própria arte desfocada; 25 s, sem narração. A versão com lupa (`zoom.py`, 1:05) foi REJEITADA: "feio, dinâmica ruim, longo" | Mandado (para_musica + com_trilha) |
| `byebye-reels/` (`curto.py`) | Trend "bye, bye, Miss American Pie": Banco Imobiliário → jogos modernos | **Vídeo curto (12 s, sem som)**: Banco Imobiliário aberto na mesa de madeira, com cor lavada, passando; no "tchan" (3,0 s) flash e vira para o Hot Streak (foto oficial) e o Ticket to Ride: Lendas do Oeste, e fecha com a Sua Vez. A versão longa com polaroides (`byebye.py`) foi REJEITADA ("ficou horrível") | Mandado |
| `tipos-reels/` (`tipos.py`) | Os 7 tipos de jogador que todo grupo tem | **Cartas colecionáveis** com raridade, status, habilidade e jogo favorito; pacotinho rasgando, carta virando, brilho holográfico | Prévia mandada; esperando a narração |
| `marvel-reels/` (`portais.py`) | Os 9 Marvel United do acervo + Multiverse chegando | **Portais do multiverso** (opção 1) com pegada de **filme de herói**: arte da capa dentro de portais de faíscas, caixas 3D e miniaturas recortadas saindo dos portais, holofote, brilho de lente, faixas de cinema e acabamento limpo em HD (sem granulado), trilha de trailer | **Narrado e entregue** (1:08, com e sem legenda; 1080p em 2 passadas a 3250k para caber em 30 MB) |

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

- **7 Wonders Arquitetos:** **narração recebida (10/out/2026)**: de novo os 9 .webm vieram SEM nome e na ordem INVERTIDA, e
  as falas 6 (vermelhas) e 7 (verdes) vieram gravadas trocadas; encaixei pela cena (cena 6 = guerra). A fala dele somou 81 s
  de vídeo: pausas internas ≤0,3 s (`encurta_pausas`), voz 1,10x (`atempo` antes da cadeia), LEAD/GAP/TAIL 0,2/0,4/0,35 e
  CTA_HOLD 2,4 → 69,9 s. A fala 9 virou "Um jogo que funciona pra casal e até 7 jogadores. Aluga o 7 Wonders Arquitetos...".
  Tela final ganhou "OU RECEBA EM CASA". Entregue a −15,5 LUFS, 2 passadas a 3000k (~28 MB). Antes era: esperando os 9 áudios. Gravador:
  `https://raw.githack.com/erik-magalhaes/GitJoy/6a9efbbc00e888124e30d4c5bd710ad1c6dd2bf6/architects-reels/gravador/Gravar_narracao_Arquitetos.html`.
  Ao receber: copie os áudios para `architects-reels/narracao/raw/`, trate (`tratar_narracao.py`), revise o `TEXTO` em
  `narracao.py`, rode `python3 narracao.py` e depois `python3 stopmo.py`, suba o volume e mande as duas versões.
  O kit de imprensa não está no repositório. Se precisar das peças de novo, baixe o zip BR e rode `pecas_oficiais.py <pasta>`.
- **Nekojima:** o dono não gostou e pediu para **apagar** o vídeo do projeto (out/2026). A pasta `nekojima-reels/` foi removida
  (fica no histórico do git). Só os sons base foram mantidos, em `comum/som_neko.py`, porque as trilhas do Hot Streak,
  do Marvel United e do hobby usam esses sons. Lição que fica: recorte só funciona com material oficial (peças com
  transparência) ou foto feita para isso (fundo liso e contrastante); antes de animar recortes, mande um quadro de teste.
- **Arte de promoção** (`promo/promo_progressivo.py` é a atual, com os degraus 3/5/7 jogos; a antiga é `promo/promo_3jogos.py`): "3 jogos = 7 dias para todos", em feed e story, com as cores e a fonte do site.
  Ele achou estranha a frase "em vez de 5, sem pagar nada a mais"; a que ficou foi "+2 dias de presente, pelo mesmo preço!".
  Os preços variam por jogo (exemplos do carrinho: Bad Company R$ 45, Art Society R$ 30 por 5 dias).
  **Flyer impresso para evento** (`promo/flyer_evento.py`, out/2026): A5 a 300 dpi (PNG + PDF) e A4 com 2 por folha; logo,
  "ALUGUE JOGOS DE TABULEIRO / e jogue em casa por 5 dias", 160 jogos a partir de R$ 15, 3 passos (reserve, retire em
  Mauá ou receba em casa, jogue 5 dias), escada 3/5/7 → 7/10/15 dias, cupom do evento **JOGAMAUA5 = 5% de desconto na
  locação** (ele disse "Joga Mauá 5") e QR code do site (conferido com o leitor do OpenCV).
  Ele achou o flyer "detalhado demais" e mandou de referência um cartãozinho de cookie (quadrado, fundo claro, uma cor,
  enfeites cortados nos cantos). Ficou `promo/cartao_evento.py`: **9 x 9 cm**, logo, "Bora jogar? / Alugue jogos de
  tabuleiro e jogue em casa por 5 dias!", QR + cupom JOGAMAUA5 5% OFF, @suavez_bg; A4 com 6 cartões e marcas de corte
  para imprimir em papel comum. Para impressos curtos: pouco texto, QR grande.
- **Hot Streak (`hotstreak-reels/`):** é da CMYK, com 4 mascotes (Hurley, o cachorro-quente; Gobbler, o urso; Dangle,
  o peixe-pescador; Mum, a rainha). São 3 corridas, 2 bilhetes por corrida em draft cobra, aposta segura ou arriscada,
  apostas paralelas SIM/NÃO e uma carta secreta de cada jogador no baralho. Mascote cai, dá meia-volta, desvia de raia e bate;
  é desclassificado se cair já caído ou sair da pista; vence quem tiver mais dinheiro. **Nomes da edição brasileira (Galápagos), confirmados pelo dono:** **Jiba** (a salsicha), **Gluglu** (o urso),
  **Brinco** (o peixe) e **Mona** (a rainha). Nunca use os nomes em inglês. Os bilhetes foram adaptados por
  `recortes_hs.bilhetes_br()` ("Gluglu" e "SIM"). Final pedido por ele: "PARA TUDO! Em quem você aposta? Comenta aqui!",
  seguido de uma corridinha (cena 9, sem fala) em que o Gluglu capota e o **Brinco ganha** na foto de chegada.
  **Material:** o manual em PDF
  (`assets/manual.pdf`) é todo vetorial. `vetor_hs.py` redesenha só os traços escolhidos e gera recortes PERFEITOS em qualquer
  resolução: os mascotes do pódio (`p_*.png`), a torcida sem o QR da editora (`v_torcida_limpa.png`) e os bilhetes. Os bonecos
  de vinil da foto oficial (Shopify da CMYK, 6000 px) recortam bem por chave de verde (`recortes_hs.py`). **Conceito escolhido:
  2, Arquibancada** (arte do jogo: torcida, pista verde, confete, placas). Teste e roteiro aprovados ("Sim").
  **Vídeo completo em `hs.py`** (66 s, 9 cenas): gancho com torcida e Hurley; largada com nomes; guichê de bilhetes
  (creme com borda vermelha e lâmpadas); bilhete virando de "Safe" para "Risky"; telão com a ilustração das cartas
  secretas e a carta entrando no baralho; corrida com casas, cartas virando embaixo (o Dealer) e legendas; DQ por queda
  dupla e por sair da pista; pilhas de dinheiro e tela VS para o "Comenta aqui!"; CTA com a caixa recortada
  (`recortes_hs.caixa()`, foto em fundo vermelho). As cartas de corrida do PDF são imagens de 151 px (pixeladas), então
  `hs.carta()` redesenha as cartas no estilo do jogo. Trilha própria: `som_hs.py` (galope, corneta, caixa registradora,
  buzina de DQ). Transição: bandeira quadriculada. A prévia foi mandada e estamos esperando os 9 áudios
  (`hs_narracao_NN`). **Narração recebida (out/2026):** a fala 7 diz "foi atropelado, desclassificado" (pelo manual,
  atropelado de pé só cai). Eu cortei o trecho e ele mandou voltar: **não mexa no que ele falou, mesmo que a regra não
  bata 100%** (no máximo avise). Voz acelerada 1,086x (atempo 1,06 × 1,025), corridinha a 62% e CTA_HOLD 2,3 → 69,5 s. **Narrado e entregue** (com e sem legenda).
  Gravador:
  `https://raw.githack.com/erik-magalhaes/GitJoy/24baf7085f0f95b8c9618b54b379541b9fecb2b5/hotstreak-reels/gravador/Gravar_narracao_HotStreak.html`.
- **Reels do hobby (`hobby-reels/`):** ele pediu um vídeo explicando os jogos modernos para quem não conhece o hobby,
  com a comparação de preço (loja × aluguel) e a promoção progressiva. Escolheu o visual 1 (estante) e pediu que **eu mesmo
  fizesse a narração, "sem cara de IA"**. Voz: `pt-BR-AntonioNeural` (edge-tts), gerada por `gerar_voz.py`. O edge-tts
  funciona pelo proxy com o CA `/root/.ccr/ca-bundle.crt` (veja `tts.py`). Para soar natural: velocidade +12–16% e tom
  variando por fala, pausas internas cortadas para ≤0,3 s (`tratar_narracao.encurta_pausas`) e escrita fonética
  ("Uíngspan"). Amostras das vozes (Antonio, Thalita, Francisca) foram mandadas e ele ficou com a primeira.
  **Resultado: ele achou as vozes "muito robóticas" e decidiu narrar ele mesmo.** Não ofereça voz sintetizada de novo
  sem ele pedir. A versão sintetizada ficou guardada em `narracao_tts/`. O fluxo voltou ao normal: prévia sem voz +
  gravador `gravador/Gravar_narracao_Hobby.html` (arquivos `hobby_narracao_NN`):
  `https://raw.githack.com/erik-magalhaes/GitJoy/bfa6b27128ef7ce4e1690c26d256c9957c564344/hobby-reels/gravador/Gravar_narracao_Hobby.html`.
  **Narração recebida (out/2026):** os 9 .webm vieram SEM nome e na ordem INVERTIDA (o 1º arquivo era a fala 9): sempre
  transcreva antes para saber de qual vídeo e de qual fala é cada um. A fala dele somou 61 s, então apertei
  LEAD/GAP/TAIL para 0,2/0,4/0,35 e CTA_HOLD para 3,0 (vídeo de 1:08). O render já sai a ≈ -14 LUFS.
  **Correções pedidas:** (1) recortes com sobra laranja (Flamecraft): resolvido "descascando" de fora para dentro as regiões
  com cor de fundo/sombra ligadas à borda antes do casco convexo; (2) **não dizer "jogo bom é caro"** (existe jogo bom e barato).
  A fala ficou "os jogos modernos costumam ser caros... por isso alugar faz tanto sentido".
  (3) Marvel United saía torto porque a foto do site é só a arte da capa, sem a caixa 3D (vale para todos os Marvel United):
  trocado por The Goonies (cooperativo). (4) A parede do final repetia caixas: agora usa `assets/acervo/` (105 caixas
  diferentes e bem recortadas, de 161; a lista está em `assets/acervo_bons.txt`, escolhida no olho, porque a medida
  automática `sobra_laranja` confunde arte laranja com sobra). Recorte em lote: `python3 recortes_caixas.py acervo`.
  **Fotos das caixas:** o site da Sua Vez (`/boardgames?page=N`) tem renders 3D de 1024 px em fundo laranja liso;
  `recortes_caixas.py` recorta com GrabCut + modelo do degradê + remoção da sombra + casco convexo. Caixas laranja
  (Cores com Dicas, Patchwork, Sushi Go, Splendor, Dinosaur Island) saem com sobra e foram descartadas.
  **Preços (out/2026):** aluguel de R$ 15, 30, 45 ou 60 por 5 dias, com 160 jogos no acervo; Wingspan a partir de R$ 377 nas lojas
  (Compara Jogos) e R$ 45 no aluguel; Clank! Catacombs a partir de R$ 422 (R$ 45); Hot Streak a partir de R$ 279 (R$ 30).
- **Marvel United (`marvel-reels/`):** ele pediu "bem recortado, numa pegada filme de heróis" e escolheu os **portais** (opção 1).
  No acervo há **3 jogos base** (Marvel United, X-Men, Spider-Geddon) e **6 expansões** (Civil War, Blue Team, Gold Team,
  Deadpool, Rise of the Black Panther, Enter the Spider-Verse), todos a R$ 30. Pedido dele: destacar que **1 base + 2 expansões
  = 3 caixas = 7 dias** (prazo progressivo). O "vilão controlado por jogador" já existe no X-Men (Modo Supervilão), então
  não é novidade do Multiverse. O Multiverse é da Galápagos (jan/2025, ~R$ 330, 1 a 5 jogadores) e "vem aí" para o acervo.
  **Material:** as fotos do site da Sua Vez são só a arte da capa (sem caixa 3D). As fotos 3D e das miniaturas em fundo branco
  vieram da Bravo Jogos (2000 px). As capas das outras expansões vieram do Compara Jogos (`og:image`). `recortes_marvel.py` faz:
  caixas 3D por flood fill + casco convexo; caixas montadas a partir da capa (frente, lateral e tampa); e miniaturas
  separadas uma a uma, tirando os vãos brancos fechados. Na mão de cartas, NÃO tire os brancos internos.
  **2ª rodada (pedido dele):** os recortes de caixa estavam ruins, então troquei pelas **fotos 3D oficiais da Spin Master/CMON**.
  As lojas Shopify publicam essas fotos: dá para buscar com `/search?q=...` e ler `/products/<handle>.json`. Usei The Game Steward,
  Gameology e Riftgate (nomes do tipo `smy..._web_box_3d_l.jpg`). O Gold Team só tem a capa, então a capa foi aplicada em
  perspectiva na foto 3D oficial da Blue Team, que tem o mesmo formato (`caixa_no_molde`). O Civil War oficial tem a lateral branca
  e o recorte falha; ficou a foto da Bravo. Cada portal mostra a caixa **de onde saem** as miniaturas (não pôr capa do X-Men com
  as miniaturas do jogo base). O gancho virou um **elenco inteiro** saindo do portal (miniaturas de várias caixas, em duas fileiras).
  **3ª rodada:** ele quis um **paredão com todas as miniaturas** ("mostrando tamanho, diferença"). Ficou em `paredao()`: 5 degraus de
  vitrine com ~49 miniaturas de 8 caixas, todas na mesma escala graças à `REF`, que dá a altura de uma miniatura comum em cada
  foto (cada foto de loja tem um zoom diferente). Fotos de miniaturas em fundo branco da Zatu (Shopify, 1024 px): Deadpool,
  Blue Team, Gold Team e Multiverse. A Zatu também tinha a caixa 3D oficial do Gold Team. As miniaturas do Multiverse saem do
  portal gigante na cena "vem aí".
  **4ª rodada:** as fichas de seta e de soco (recortadas em ângulo de uma foto da Bravo) ficaram tortas e ruins. Agora uso os
  **ícones oficiais de ação** do manual da CMON (`https://cmon-files.s3.amazonaws.com/pdf/assets_item/resource/202/Marvel_United_Rulebook.pdf`,
  pág. 8): `icones_oficiais.py` troca a textura de papel do fundo por uma imagem transparente e renderiza a página com alfa a 1000 dpi
  (os ícones têm degradê, então o redesenho traço a traço do Hot Streak não serve). Resultado: `icone_{mover,atacar,heroica,coringa}.png`.
  **Dica geral:** para símbolos de jogo, o manual oficial em PDF é a melhor fonte.
  Gravador: `https://raw.githack.com/erik-magalhaes/GitJoy/3d0afc99e9c3cdc65a416b73ad54dfbbcbe784b3/marvel-reels/gravador/Gravar_narracao_Marvel.html`.
- **Qualidade de imagem (lição do Marvel United):** ele NÃO gosta de granulado de filme nem de nada que pareça ruído ou
  pixel ("quero HDzão de cinema"). Use acabamento limpo: vinheta suave, movimento liso a 30 fps no estilo trailer (sem tremidinho),
  luz de recorte fina e nítida (sem halo borrado), recortes passados por `fastNlMeansDenoisingColored` + `UnsharpMask`
  (tira os bloquinhos de JPEG das fotos de loja), x264 com `-crf 16 -tune film` e prévia 720p a ~6000k em fundos escuros
  com degradê (a 2800k aparece blocagem). O chat aceita arquivos de no máximo 30 MB: para ~66 s, use x264 em duas passadas
  a ~3300k (`-preset slow -tune film -pass 1/2`), que fica com ~28 MB.
- **Engajamento (out/2026):** ele reclamou de visualizações e engajamento baixos. Explicar regras não gera marcação nem
  comentário; os formatos novos são entretenimento: **marcar o amigo** (tipos de jogador), **quiz** (palpite nos comentários,
  assistir de novo) e **trend com música em alta**. Vídeo para música em alta: SEM narração, tudo escrito na tela, entregue
  em duas versões: `_para_musica` (só efeitos, ele põe o áudio da trend no Instagram) e `_com_trilha` (reserva).
  No quiz ele pediu jogos **mais difíceis** e escolheu a lista: Ticket to Ride, King of Tokyo, Codinomes (no acervo é o
  **Código Secreto Imagens**), Deep Regrets e Segue o Fluxo. O zoom nunca pode mostrar o título nem a borda da caixa.
  Trend: vídeo de trend é CURTO (ele disse que não precisa de 1 minuto) e a ação tem que bater com a música; a ideia boa
  foi dele: jogo antigo → "tchan" → jogo moderno. Eu não tenho acesso à música (direitos autorais): ele põe o áudio no
  Instagram. Se ele mandar o áudio da trend (gravação de tela), dá para achar o tempo exato do "tchan" e mudar `VIRADA`.
  **A trend é o "efeito Suíça"** (referência em `byebye-reels/referencia/`, fora do git): "antes" feio (calçada esburacada)
  até o silêncio da música, e no "tchan" (a música volta em 10,16 s; corte em 10,10 s) vira o "depois" bonito (Suíça), com
  o texto fixo 'O efeito "Suíça" 🇨🇭' (branco, contorno preto, y≈660). Cortes medidos: antes 0 / 4,67; depois 10,10 / 12,47 /
  14,40 / 16,43; fim 22,17. `byebye-reels/efeito.py --antigo ... --moderno ...` monta tudo com os clipes dele e o áudio da
  referência ('O efeito "jogos modernos" 🎲'), em versão com e sem música.
  **Feito (1ª versão):** ele gravou 5 clipes no celular (HEVC 1080p girado; em `referencia/clipes/`, fora do git):
  c1 Quest e c2 Imagem & Ação (antigos), c3 Santorini, c4 Luxor e c5 Hot Streak (modernos). Comando usado:
  `python3 efeito.py --planos c1.mp4:2.0 c2.mp4:0.5 c3.mp4:0.3 c4.mp4:1.6 c4.mp4:4.6 c5.mp4:2.0` (os caminhos estão em
  referencia/clipes). Cor (`grade()`, pedido dele "dar um tchanzão"): denoise + normalize + curva em S + correção do amarelo
  da lâmpada + nitidez nos dois; no depois, vibrance, bloom suave, vinheta leve e flash branco de 0,3 s no "tchan". Saída com e sem música, 22 s, ~26 MB.
  Fotos: Banco Imobiliário aberto do site da Estrela (`estrela.fbitsstatic.net/img/p/banco-imobiliario-150398/336914-1.jpg`),
  Ticket to Ride Lendas do Oeste da Gameology (Shopify), Hot Streak `hotstreak-reels/assets/fotos/HS4751.jpg`.
  Código comum dos três: `comum/motor.py` (animação, textos, legendas, render, prévia) e `comum/som.py` (trilhas
  gameshow/travessa/retro70 e efeitos). Emojis coloridos: Noto Color Emoji (`motor.emoji`). Vídeos de animação a 1080p
  ficam com < 30 MB, então dá para mandar o 1080p direto no chat.
  Caixas laranja do site (fundo laranja) recortam mal no automático: Código Secreto e Deep Regrets foram recortados à mão
  com um polígono de 6 pontos (caixa 3D) em `hobby-reels/assets/caixas/`.
  **7 tipos:** gravador `tipos-reels/gravador/Gravar_narracao_Tipos.html` (arquivos `tipos_narracao_NN`):
  `https://raw.githack.com/erik-magalhaes/GitJoy/5da0dc105532cf7d29b3ef270d4c72a131ff5c29/tipos-reels/gravador/Gravar_narracao_Tipos.html`.
  Ao receber: `narracao/raw/` → tmp_NN.wav (cadeia de voz) → `tratar_narracao.py` → revisar `TEXTO` → `narracao.py` → `tipos.py`.
- **Vídeos GRAVADOS pelo dono (`gravados-reels/`, out/2026):** ele grava falando para a câmera + cenas dos jogos, eu edito.
  Arquivo grande: ele sobe numa pasta do **Google Drive** pública e eu baixo com `pip install gdown; python3 -m gdown <link da pasta>`
  (funciona pelo proxy). Brutos ficam em `gravados-reels/brutos/` (fora do git). `criancas.py` (jogos para crianças, ~35 s):
  falas boas cortadas da tomada longa (ele erra e repete; uso a última tentativa boa), rosto dele 1,7 s e corte para as cenas
  do jogo com a fala por cima, legenda, "comenta" e CTA com mosaico das cenas dele. Pedidos dele: **qualidade de luz, som e
  edição**; imagem por cima só se for **oficial** (nunca recorte do site); o gancho é a cena dele **pertinho do celular
  ajeitando a câmera** (a ÚLTIMA aproximação do `vg.mp4`, 8,45–11,15 s) com `camera()`: aproxima 10% devagar e abre
  rápido com desfoque de movimento quando ele se afasta; depois ele fala "A gente separou quatro ótimos jogos…" e entra
  uma montagem rápida dos 4 jogos. **1ª versão REJEITADA ("áudio horrível, jogos super estourados, refaz tudo"):**
  EQ forte na voz (+5 dB de agudo, aexciter, agate) soou artificial, e normalize + curvas + vibrance estouraram os brancos
  (de ~0% para 5% de pixels ≥250) e a saturação (+60–75%). **2ª versão:** voz só com highpass 75 Hz, −2 dB em 300 Hz,
  compressão leve 2:1 e loudnorm; cor só com `eq` leve (contraste 1,03, saturação 1,05) + denoise e nitidez fracos;
  trilha mais baixa (`musica_ganho=0.2`, `duck=0.8` em `som.build`). **Lição: em vídeo gravado, mexa pouco; meça
  estouro (% ≥250) e saturação contra o bruto antes de mandar.** 39 s, com e sem legenda, 2 passadas a 5200k para o chat.
  **3ª rodada ("voz de Darth Vader", "só cortou e colou"):** a voz saía em 48 kHz e `read_wav` toca a 44,1 kHz → 9% mais
  lenta e grave e fora de sincronia. **Extraia a voz SEMPRE com `-ar 44100`.** Também havia buraco de 0,2 s entre planos
  (imagem adiantada); cortes agora por quadros exatos (`nq()`). Edição que ele pediu, por jogo: rosto dele LIVRE (nada
  escrito na frente do rosto) → a capa OFICIAL pequena no canto de baixo à direita quando ele FALA o nome (tempo do
  Whisper) → o vídeo do jogo na mesa em tela cheia com nome + fichas (tipo, jogadores, idade, tempo) → volta pra ele, ainda
  com a capa. Cada trecho de cena só UMA vez. Legenda palavra a palavra (1–3 palavras, a falada em amarelo, `palavras.json`).
  **Capas da edição ATUAL/brasileira** (ele cobrou): Go Cuckoo é a da **Devir (2023, 5+)**, foto da Bravo Jogos; Draftosaurus
  da **MeepleBR** (site da editora, wp-content); Gravity Superstar (Sit Down!) e Scooby-Doo (CMON) têm a mesma capa da dele.
  Compara Jogos (`/item/<slug>`, og:image) às vezes traz a edição estrangeira: confira contra a caixa que aparece no vídeo dele.
  **4ª rodada:** ele quer MAIS jogo na tela: o rosto dele só na apresentação (até ~0,9 s depois de dizer o nome) e daí
  até o fim da fala só as cenas do jogo (2 por jogo) + `RESPIRO` de 0,7 s antes do próximo; sem voltar pro rosto.
  Giro dele no começo do Scooby: ele disse para DEIXAR ("não ficou horrível"). **Som de microfone de lapela/sem fio dele:**
  chega muito grave/abafado e muito alto; o que soava "esquisito" era o loudnorm dinâmico bombeando e o `tanh` da
  mixagem saturando a voz. Receita: EQ moderada (−4 dB em 320 Hz, −2 em 140, +2 em 3,2 kHz, shelf +2 em 6 kHz), ganho
  FIXO por fala (`nivela`), `som.build(..., satura=False)` e loudnorm LINEAR em 2 passadas no final (`final_loudness`).
  **5ª rodada (`criancas2.py`, gravação nova em `brutos/novos/`):** gancho novo (182144) e todas as falas numa tomada
  (182216), usando a ÚLTIMA tentativa boa de cada uma (cortes conferidos transcrevendo cada pedaço). Ele: "no celular a
  100% o som explode, um pouco mais baixo fica bom" → loudness final **−15,5 LUFS com pico −2 dB**. Edição "adulta":
  sem emoji de balão no gancho; efeitos discretos do jogo por cima das cenas da mesa (`efeitos()`): ovos caindo (Go
  Cuckoo), estrelas brilhando (Gravity), pegadas subindo pela direita (Draftosaurus), névoa + fantasma (Scooby; ele pediu para TIRAR o "ZOINKS!").
  Rosto sem punch-in (o boné cortava). Final: "comenta" → ele falando o CTA ("Todos esses jogos já estão disponíveis lá
  na Sua Vez...") → tela final. 48 s.
  **6ª rodada:** (1) o gancho começa com ele JÁ mexendo na câmera (1,85 s do 182144), não indo até ela; (2) **nunca
  começar um corte na puxada de ar**: o início de cada fala é a 1ª palavra, medida pela energia (salto para > −25 dB
  depois do respiro/estalo); (3) acabamento "HD" sem estourar cor: hqdn3d forte + curva que segura os brancos (estouro
  ~5% → 0,3%) + unsharp só na luz + vinheta PI/14 + saturação 0,95–0,97 e gamma 1,04 (conferir estouro, saturação e
  brilho contra o bruto). 45 s, −15,4 LUFS, pico −3 dB.
  Vídeos gravados podem ter menos de 1 minuto.
- **Final Girl (`finalgirl-reels/`, out/2026):** ele tem a Caixa Base + a 1ª temporada (Hans, Poltergeist, Inkanyamba,
  Geppetto e **Dr. Medo**). Escolheu o **visual 2, Trailer Slasher** (`conceitos.py`): tela escura com névoa lisa, facho
  de lanterna revelando as artes (`no_escuro`), títulos em Creepster vermelho com brilho, relâmpagos, faixas de cinema e
  trilha de trailer de terror (`som_fg.py`: drone, coração que acelera, braam, trovão, stinger). Script: `trailer.py`.
  **Edição BRASILEIRA = Ludofun** (store.ludofun.com.br; fotos 1200 px em fundo branco, CDN awsli): Caixa Base, O Terror em
  Happy Trails (Hans), A Assombração da Mansão Creech (Poltergeist), Massacre nos Bosques (Inkanyamba), Carnificina no
  Circo (Geppetto) e Terror em Maple Lane (Dr. Medo). Recortes em `recortes_br.py`; a arte de cada assassino vem do
  tabuleiro oficial da Van Ryder (`FFn-compview.png`, só a arte, sem os textos em inglês) e o Hans grande do verso da caixa.
  Artes retangulares precisam de borda esfumada (`esfuma`) senão aparece o retângulo no escuro.
  **Regras conferidas** (manual/Zatu): dados = nível de Horror; 5 ou 6 = sucesso (3–4 = parcial, descartando 2 cartas);
  cada vítima morta sobe a Sede de Sangue do assassino; o Final é revelado quando o baralho do Terror acaba; vence quem
  mata o assassino. Caixa: 1 jogador, 20–60 min, 14+. Prévia mandada; gravador (arquivos `finalgirl_narracao_NN`):
  `https://raw.githack.com/erik-magalhaes/GitJoy/2cdb54d81a82415bb8f545a35b43ad98a6f5dea2/finalgirl-reels/gravador/Gravar_narracao_FinalGirl.html`.
  Ao receber: `narracao/raw/` → tmp_NN.wav → `tratar_narracao.py` → revisar `TEXTO` → `narracao.py` → `trailer.py`.
- `architects-reels/arq.py` (planta azul) e `mlem-reels/mlem.py`/`stopmo.py` são versões **rejeitadas**. Ficam só como referência.
