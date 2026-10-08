# Reels da Sua Vez – memória do projeto

Este repositório reúne os vídeos verticais (Reels/TikTok) dos jogos de tabuleiro da **Sua Vez**. Leia
tudo antes de começar um vídeo novo: aqui está o que funcionou, o que não funcionou e do que o dono gostou.

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
| `architects-reels/` (`stopmo.py`) | 7 Wonders Arquitetos | **Stop motion** com as peças oficiais sobre **papel quadriculado** (tema "prancheta"), com textos em fita crepe escritos à mão | Prévia aprovada; falta a narração |
| `hobby-reels/` (`ludoteca.py`) | Institucional: o que são jogos modernos + preço loja × aluguel + prazo progressivo | **Estante da ludoteca** (opção 1): caixas do acervo em prateleiras de madeira, caixas saindo em stop motion, etiquetas kraft e de preço | Prévia mandada; esperando a narração dele |
| `marvel-reels/` (`portais.py`) | Os 9 Marvel United do acervo + Multiverse chegando | **Portais do multiverso** (opção 1) com pegada de **filme de herói**: arte da capa dentro de portais de faíscas, caixas 3D e miniaturas recortadas saindo dos portais, holofote, brilho de lente, granulado e faixas de cinema, trilha de trailer | Prévia mandada; esperando a narração |

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
- **Nekojima:** o conceito escolhido foi o **ANIME** (opção 2). Eu fiz por engano a "transmissão esportiva"
  (`neko.py`, rejeitada), e a versão certa é `nekojima-reels/anime.py`. Ela reaproveita o roteiro, as cenas, as legendas e a
  narração do `neko.py`, e tem: painel inclinado de borda branca, linhas de velocidade a 12 poses/s, onomatopeias japonesas
  (fonte Dela Gothic One), sakura, quadro de impacto, card "猫島 Episódio 1", tela VS e trilha de abertura de anime
  (`som_neko.build(estilo="anime")`). A prévia foi mandada. Ofereci também deixar as fotos com cara de desenho (cel-shading:
  bilateral + k-means + contorno), e o teste está em `out/teste_fotos_anime.jpg`; falta a resposta. Esperando os 9 áudios
  (`neko_narracao_NN`). Gravador:
  `https://raw.githack.com/erik-magalhaes/GitJoy/363f36067a019067175e2815c7d6d7a7648fc1e4/nekojima-reels/gravador/Gravar_narracao_Nekojima.html`.
  **Lição:** quando ele disser o número da opção que prefere, use exatamente essa e confirme antes de produzir.
  **Versão atual: `anime_rec.py`.** Ele gostou do anime, mas reclamou que as fotos inteiras deixam o vídeo parado e "com cara
  de foto da internet". Agora as peças são recortadas (`recortes_neko.py`: torre, gato, poste, marcador de nível, faces dos dados
  e textura de madeira) e se mexem: a torre balança e desaba, os dados quicam, o gato voa até o fio e balança, o poste cai e
  encaixa e os cubos pulam. **Resultado: ele achou HORRÍVEL** ("os recortes estão horríveis"). Recortar de foto de produto
  em fundo branco não funciona para este jogo: os fios finos (sobretudo os brancos) somem, a torre fica falhada, o gato fica
  serrilhado, e os dados "montados" com a textura e as faces parecem falsos. **Não insista nesse caminho.** O Nekojima não tem
  kit de imprensa público (o site da Unfriendly Games dá 502 pelo proxy). Propus que ele mesmo fotografe as peças (stop motion
  real com o jogo da loja) ou que eu volte ao anime com as fotos inteiras. **Decisão: ficou o `anime.py` (fotos inteiras),
  como estava.** A única mudança foi corrigir o texto da face especial do dado ("FACE PRETA? QUEM ESCOLHE É O DA DIREITA!").
  `anime_rec.py` (recortes) está rejeitado.
  **Regra geral:** recorte só funciona com material oficial (peças com transparência) ou foto feita para isso (fundo liso
  e contrastante). Antes de animar recortes, mande um quadro de teste e espere o ok dele.
  A face especial do dado é **preta com adaga** (o torii roxo é um bairro).
- **Arte de promoção** (`promo/promo_progressivo.py` é a atual, com os degraus 3/5/7 jogos; a antiga é `promo/promo_3jogos.py`): "3 jogos = 7 dias para todos", em feed e story, com as cores e a fonte do site.
  Ele achou estranha a frase "em vez de 5, sem pagar nada a mais"; a que ficou foi "+2 dias de presente, pelo mesmo preço!".
  Os preços variam por jogo (exemplos do carrinho: Bad Company R$ 45, Art Society R$ 30 por 5 dias).
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
  (`hs_narracao_NN`). Gravador:
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
  Gravador: `https://raw.githack.com/erik-magalhaes/GitJoy/3d0afc99e9c3cdc65a416b73ad54dfbbcbe784b3/marvel-reels/gravador/Gravar_narracao_Marvel.html`.
- **Qualidade de imagem (lição do Marvel United):** ele NÃO gosta de granulado de filme nem de nada que pareça ruído ou
  pixel ("quero HDzão de cinema"). Use acabamento limpo: vinheta suave, movimento liso a 30 fps no estilo trailer (sem tremidinho),
  luz de recorte fina e nítida (sem halo borrado), recortes passados por `fastNlMeansDenoisingColored` + `UnsharpMask`
  (tira os bloquinhos de JPEG das fotos de loja), x264 com `-crf 16 -tune film` e prévia 720p a ~6000k em fundos escuros
  com degradê (a 2800k aparece blocagem).
- `architects-reels/arq.py` (planta azul) e `mlem-reels/mlem.py`/`stopmo.py` são versões **rejeitadas**. Ficam só como referência.
