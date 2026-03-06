## Protocolo de Encriptação Temporizada por Custo — Formalização

---

### Visão Geral

Um arquivo $F$ é encriptado com AES-256-GCM usando uma chave $K$ derivada via HMAC-SHA256 de uma **semente curta** $S$ de $n$ bits. Um hash $V = \text{HMAC-SHA256}(S,\ n)$ é publicado como **compromisso de verificação** — qualquer um pode testar candidatos contra $V$ sem precisar do arquivo. A chave é derivada encadeando: $K = \text{HMAC-SHA256}(S,\ V)$. Um único protocolo (HMAC-SHA256) para tudo.

---

### Parâmetros de Entrada

| Símbolo | Tipo | Descrição |
|---------|------|-----------|
| $F$ | $\{0,1\}^*$ | **File** — arquivo original em bytes |
| $T$ | $\mathbb{R}^+$ | **Time** — tempo alvo em anos |
| $t_0$ | $\mathbb{N}$ | **Time zero** — ano de criação do puzzle |

---

### Construção do Puzzle

**Passo 1 — Calcular a dificuldade:**

$$n = \mathcal{B}(t_0,\ \$1\text{M}) + \lfloor \log_2(T) \rfloor$$

| Parte | Significado |
|-------|-------------|
| $n$ | Tamanho da semente em bits — define a dificuldade do puzzle |
| $\mathcal{B}(t_0, \$1\text{M})$ | Bits que $\$1\text{M}$ em GPUs quebra em $t_0$ rodando por 1 ano |
| $T$ | Tempo alvo em anos — fator de escala temporal |
| $\lfloor \log_2(T) \rfloor$ | Converte o fator multiplicativo em bits adicionais (positivo ou negativo) |

> Intuição: $\mathcal{B}$ define quantos bits $\$1\text{M}$/ano alcança hoje. $T > 1$ ano soma bits (mais dificuldade); $T < 1$ ano subtrai bits (menos dificuldade). Duplicar $T$ adiciona +1 bit.

**Passo 2 — Gerar a semente:**

$$S \xleftarrow{\$} \{0,1\}^n$$

| Parte | Significado |
|-------|-------------|
| $S$ | **Seed** — semente aleatória de $n$ bits; é o segredo do puzzle |
| $\xleftarrow{\$}$ | Amostragem uniforme aleatória (o cifrão indica aleatoriedade criptográfica) |
| $\{0,1\}^n$ | Conjunto de todas as strings binárias de comprimento $n$ |

**Passo 3 — Hash de verificação:**

$$V \leftarrow \text{HMAC-SHA256}(S,\ n)$$

| Parte | Significado |
|-------|-------------|
| $V$ | **Verification hash** — compromisso público de $S$; permite verificar sem o arquivo |
| $\text{HMAC-SHA256}$ | Código de autenticação baseado em hash — RFC 2104 |
| $S$ | Chave do HMAC (o segredo) |
| $n$ | Mensagem do HMAC (parâmetro público) |

**Passo 4 — Derivar a chave:**

$$K \leftarrow \text{HMAC-SHA256}(S,\ V)$$

| Parte | Significado |
|-------|-------------|
| $K$ | **Key** — chave AES de 256 bits derivada do encadeamento $S \to V \to K$ |
| $S$ | Chave do HMAC (mesmo segredo) |
| $V$ | Mensagem do HMAC (output do passo anterior) |

> Mesmo protocolo do Passo 3, com mensagem diferente. $V$ alimenta $K$ — encadeamento natural.

**Passo 5 — Encriptar o arquivo:**

$$C \leftarrow \text{AES-256-GCM}(K,\ F)$$

| Parte | Significado |
|-------|-------------|
| $C$ | **Ciphertext** — arquivo encriptado + authentication tag GCM |
| $\text{AES}$ | **Advanced Encryption Standard** — cifra de bloco simétrica |
| $256$ | Tamanho da chave em bits |
| $\text{GCM}$ | **Galois/Counter Mode** — encriptação autenticada (confidencialidade + integridade) |

**Passo 6 — Publicar:**

$$(C,\ n,\ V)$$

| Parte | Significado |
|-------|-------------|
| $C$ | Ciphertext (contém o tag GCM embutido) |
| $n$ | Número de bits da semente — informa o espaço de busca |
| $V$ | Hash de verificação — permite testar candidatos sem decriptar |

---

### Como o Atacante Quebra

**Fase 1 — Busca (rápida, sem o arquivo):**

$$\forall\ S' \in \{0,1\}^n: \quad \text{HMAC-SHA256}(S',\ n) \stackrel{?}{=} V$$

Cada teste é um único HMAC-SHA256.

**Fase 2 — Decriptação (uma única vez, quando encontrar $S'$):**

$$V \leftarrow \text{HMAC-SHA256}(S',\ n)$$
$$K \leftarrow \text{HMAC-SHA256}(S',\ V)$$
$$F \leftarrow \text{AES-256-GCM.Dec}(K,\ C)$$

Custo esperado: $2^n$ avaliações de HMAC-SHA256. Cada tentativa é independente — **busca puramente paralela**.

---

### Fórmula de Custo

O custo para quebrar **em 1 ano** com o melhor hardware (GPUs) disponível:

$$\boxed{ \text{Custo}(n,\ t_0) = \$1\text{M} \times 2^{(n - \mathcal{B}(t_0))} }$$

Como $n = \mathcal{B} + \lfloor \log_2(T) \rfloor$, isso simplifica para $\text{Custo} \approx \$1\text{M} \times T$.

**Exemplos com $t_0 = 2026$, $\mathcal{B}(2026) = 67$:**

| Tempo alvo $T$ | $\lfloor \log_2(T) \rfloor$ | Bits $n$ | Custo em 1 ano |
|---------------|----------------------------|----------|----------------|
| 1 semana | −5 | 62 bits | ~$31.250 |
| 1 mês | −3 | 64 bits | ~$125.000 |
| 6 meses | −1 | 66 bits | ~$500.000 |
| 1 ano | 0 | 67 bits | $1.000.000 |
| 10 anos | +3 | 70 bits | ~$8.000.000 |
| 50 anos | +5 | 72 bits | ~$32.000.000 |
| 100 anos | +6 | 73 bits | ~$64.000.000 |

> A escala é **linear em dólares mas logarítmica em bits** — duplicar o tempo alvo adiciona apenas 1 bit mas dobra o custo.

---

### Propriedades do Protocolo

- **Verificação sem o arquivo** — $V$ permite provar que $S'$ é a solução sem precisar de $C$
- **Um único protocolo** — HMAC-SHA256 para verificação e derivação de chave
- **Não há custódio** — nenhum terceiro guarda $S$; ele existe apenas como espaço de busca
- **Verificável publicamente** — qualquer um com $V$ pode confirmar que um $S'$ é a solução
- **Custo previsível** — a função $\mathcal{B}$ permite estimar o custo de quebra em qualquer ano futuro
- **Degradação natural** — à medida que hardware evolui, o custo de quebra cai; isso é **intencional** e quantificável
- **Busca puramente paralela** — cada tentativa é independente; escala linearmente com hardware

---

## Benchmark de Poder Computacional por Busca Exaustiva

---

### Motivação

Comparar poder computacional ao longo do tempo exige uma tarefa de referência que seja:

1. **Computacionalmente mensurável** — custo teórico bem definido
2. **Sem atalhos algorítmicos** — não melhorável por criptoanalise
3. **Paralelizável linearmente** — dobrando hardware, dobra o progresso

A busca exaustiva sobre HMAC-SHA256 satisfaz essas propriedades: cada candidato exige uma avaliação de HMAC, sem atalho possível. O hardware relevante são **GPUs** — ASICs de Bitcoin (SHA-256d) não suportam HMAC-SHA256.

---

### O Benchmark $\mathcal{B}(t, D)$

Seja:

- $t$ — ano de referência
- $D$ — orçamento em dólares
- $P(t, D)$ — número total de tentativas (HMAC-SHA256) executáveis com orçamento $D$ no ano $t$, rodando por 1 ano contínuo
- $\mathcal{B}(t, D)$ — maior $n$ tal que $2^n \leq P(t, D)$

$$\mathcal{B}(t, D) = \lfloor \log_2 P(t, D) \rfloor$$

**Interpretação:** $\mathcal{B}(t, D)$ é o número máximo de bits de semente que o orçamento $D$ no ano $t$ consegue buscar exaustivamente em 1 ano.

---

### Aproximação Contínua de $\mathcal{B}$

A tabela histórica (1945–2025) é discreta. Para uso programático e extrapolação, aproximamos $\mathcal{B}(t, \$1\text{M})$ por uma **função logística** ajustada por mínimos quadrados:

$$\boxed{ \mathcal{B}(t) = \frac{L}{1 + e^{-k(t - t_{\text{mid}})}} + b }$$

| Parâmetro | Valor | Significado |
|-----------|-------|-------------|
| $L$ | $141{,}54$ | Amplitude da curva (range em bits) |
| $k$ | $0{,}0233$ | Taxa de crescimento |
| $t_{\text{mid}}$ | $1925{,}9$ | Ponto de inflexão (metade do crescimento) |
| $b$ | $-61{,}03$ | Offset base |

**Propriedades da aproximação:**

- **MSE = 2,13** contra os 23 pontos da tabela histórica (RMSE $\approx 1{,}5$ bits)
- **Assíntota superior:** $L + b \approx 80$ bits — limite natural do hardware GPU acessível com $\$1\text{M}$
- **Assíntota inferior:** $b \approx -61$ bits — converge a zero para épocas pré-computacionais
- **Ponto de inflexão:** $t_{\text{mid}} = 1925{,}9$ — crescimento centrado no século XX
- **Estagnação recente:** a partir de ~2016, o custo/hash em GPUs estabilizou (~67 bits). GPUs ficam mais rápidas mas proporcionalmente mais caras

> A curva logística captura a forma de S dos dados: crescimento lento (1940s–70s), aceleração (1980s–2010s), e estagnação (2016+). ASICs de Bitcoin não se aplicam a HMAC-SHA256.

---

### Definição de Equivalência Temporal

Dado $\mathcal{B}(t_1, D) = b_1$ e $\mathcal{B}(t_2, D) = b_2$, o custo em $t_2$ para replicar o poder de $t_1$ é:

$$C(t_1 \to t_2) = D \cdot 2^{b_1 - b_2}$$

**Exemplo:** $\mathcal{B}(1980, 1\text{M}) = 48$ e $\mathcal{B}(2025, 1\text{M}) = 67$

$$C(1980 \to 2025) = \$1\text{M} \cdot 2^{48-67} = \$1\text{M} \cdot 2^{-19} \approx \$1{,}91$$

---

### Propriedades do Benchmark

**Monotonicidade esperada:** $\mathcal{B}(t+1, D) \geq \mathcal{B}(t, D)$ — o poder só cresce ou mantém.

**Violações detectam anomalias reais:** quedas em $\mathcal{B}$ (como 2000→2005 na tabela) indicam transições tecnológicas — de benchmarks genéricos para SHA-256 real — não ruído do benchmark.

**Independência de domínio:** o mesmo $\mathcal{B}$ serve para criptografia, IA, simulação — qualquer campo onde o custo computacional importa.

---

### Aplicações

- **Parametrização de esquemas criptográficos:** definir $n$ baseado no ano de implantação e vida útil esperada do sistema
- **Protocolo de revelação temporizada:** o prazo é expresso em bits de $\mathcal{B}$, não em tempo absoluto, tornando-o robusto a avanços de hardware




(ISSO DEVE PERMANECER INTACTO)

| Ano | Hardware | H/s por unidade | Preço | Unidades/$1M | Total H/s | Hashes/ano | Bits | Custo em 2025 p/ igualar |
|-----|----------|-----------------|-------|-------------|-----------|------------|------|--------------------------|
| 1945 | ENIAC | 5 | $6M | 0.16 | 0.8 | 2.5×10⁷ | 24 | $0.000000113687 |
| 1950 | UNIVAC I | 100 | $1M | 1 | 100 | 3.15×10⁹ | 31 | $0.0000145519 |
| 1955 | IBM 704 | 1K | $2M | 0.5 | 500 | 1.58×10¹⁰ | 33 | $0.0000582077 |
| 1960 | IBM 7090 | 10K | $3M | 0.33 | 3.3K | 1.04×10¹¹ | 36 | $0.000465661 |
| 1965 | IBM 360/50 | 50K | $1M | 1 | 50K | 1.58×10¹² | 40 | $0.00745058 |
| 1970 | PDP-11 | 100K | $100K | 10 | 1M | 3.15×10¹³ | 44 | $0.119209 |
| 1975 | VAX-11/780 | 500K | $200K | 5 | 2.5M | 7.88×10¹³ | 46 | $0.476837 |
| 1980 | 8086 PC | 50K | $5K | 200 | 10M | 3.15×10¹⁴ | 48 | $1.90735 |
| 1985 | 386 | 200K | $4K | 250 | 50M | 1.58×10¹⁵ | 50 | $7.62939 |
| 1990 | 486 DX | 5M | $3K | 333 | 1.67G | 5.26×10¹⁶ | 55 | $244.14 |
| 1995 | Pentium | 50M | $2K | 500 | 25G | 7.88×10¹⁷ | 59 | $3,906.25 |
| 2000 | P3 1GHz | 500M | $1K | 1000 | 500G | 1.58×10¹⁹ | 63 | $62,500.00 |
| 2005 | P4 3GHz ¹ | 5M | $500 | 2000 | 10G | 3.15×10¹⁷ | 58 | $1,953.13 |
| 2008 | Core2 Quad | 20M | $300 | 3333 | 66.7G | 2.1×10¹⁸ | 60 | $7,812.50 |
| 2010 | GTX 480 ² | 200M | $500 | 2000 | 400G | 1.26×10¹⁹ | 63 | $62,500.00 |
| 2012 | GTX 680 | 400M | $500 | 2000 | 800G | 2.52×10¹⁹ | 64 | $125,000.00 |
| 2014 | GTX 980 | 800M | $550 | 1818 | 1.45T | 4.59×10¹⁹ | 65 | $250,000.00 |
| 2016 | GTX 1080 | 1.5G | $600 | 1666 | 2.5T | 7.88×10¹⁹ | 66 | $500,000.00 |
| 2018 | RTX 2080 | 2.5G | $700 | 1428 | 3.57T | 1.13×10²⁰ | 66 | $500,000.00 |
| 2020 | RTX 3080 | 4.5G | $700 | 1428 | 6.42T | 2.03×10²⁰ | 67 | $1,000,000.00 |
| 2022 | RTX 3090 Ti | 6G | $1K | 1000 | 6T | 1.89×10²⁰ | 67 | $1,000,000.00 |
| 2024 | RTX 4090 | 10G | $1.6K | 625 | 6.25T | 1.97×10²⁰ | 67 | $1,000,000.00 |
| 2025 | RTX 5090 ³ | 15G | $2K | 500 | 7.5T | 2.37×10²⁰ | 67 | $1,000,000.00 ⁴ |

¹ Queda de 63→58: transição de operações genéricas para SHA-256 real — CPUs P4 são ineficientes para hash criptográfico.
² Início da era GPU: GPUs passam a dominar o custo/hash para HMAC-SHA256.
³ Estimativa baseada em ~1.5× performance da geração anterior, ~1.25× o preço.
⁴ Por definição, $1M — é o próprio benchmark de referência.

---

Leituras notáveis:

- O ENIAC de 1945 custou $6M — sua capacidade de hash equivalente hoje custa $0.000000113687.
- O que um IBM 360 fazia com $1M em 1965 (40 bits) custa hoje $0.007 — menos de 1 centavo.
- A queda de 2005 (63→58 bits) marca a transição de benchmarks genéricos → medição real de SHA-256 em CPUs.
- A partir de 2016, o custo/hash estagnou: GPUs mais rápidas, mas proporcionalmente mais caras. O teto de ~67 bits por $1M/ano é estável.
- Cada bit a mais na coluna "Custo em 2025" representa exatamente o dobro — a escala é exponencial.
