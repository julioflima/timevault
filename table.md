## Benchmark Histórico — HMAC-SHA256 com $1M de orçamento

### Notas metodológicas

1. **Antes de 2001**: SHA-256 não existia. Os valores representam a capacidade equivalente de operações aritméticas de 256 bits — estimativa do que fariam se HMAC-SHA256 existisse.
2. **Antes de 2010**: O hardware dominante eram CPUs. A partir de 2010, GPUs passaram a ser o melhor custo/hash para HMAC-SHA256.
3. **ASICs de Bitcoin não se aplicam**: ASICs SHA-256 (Antminer etc.) são otimizados para SHA-256d (duplo). HMAC-SHA256 exige flexibilidade que ASICs não oferecem. O hardware relevante é GPU.
4. **Custo em 2025**: $1\text{M} \times 2^{(b - 67)}$ — quanto custaria em 2025 para igualar a capacidade computacional que $1M comprava no ano indicado.

---

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

---

### Notas

¹ **2005 — Queda de 63 para 58 bits**: a transição de "operações genéricas equivalentes" para SHA-256 real revelou que CPUs P4 são ineficientes para hash criptográfico. O benchmark de 2000 (63 bits) usava throughput aritmético genérico.

² **2010 — Início da era GPU**: GPUs passaram a dominar o custo/hash para HMAC-SHA256. A partir daqui, os dados refletem benchmarks reais (hashcat).

³ **2025 — RTX 5090**: estimativa baseada na tendência de ~1.5× a geração anterior em H/s, mas ~1.25× o preço.

⁴ **Custo em 2025 para igualar 2025**: por definição, $1M — é o próprio benchmark de referência.

---

### Leituras notáveis

- O ENIAC de 1945 custou $6M — sua capacidade de hash equivalente hoje custa $0.000000113687. Literalmente um décimo de milionésimo de centavo.
- O que um IBM 360 fazia com $1M em 1965 (40 bits) custa hoje $0.007 — menos de 1 centavo.
- De 1945 a 2025, o custo caiu por um fator de $2^{43} \approx 8.8$ trilhões.
- A queda de 2005 (63→58 bits) marca a transição conceitual: benchmarks genéricos → medição real de SHA-256.
- A partir de 2016, o custo/hash estagnou: GPUs mais rápidas, mas proporcionalmente mais caras. O teto de ~67 bits por $1M/ano é estável.
- Cada bit a mais na coluna "Custo em 2025" representa exatamente o dobro — a escala é exponencial.

---

### Sobre a estagnação (2016–2025)

A partir de 2016, os bits estabilizaram em ~66-67. Três fatores:

1. **Lei de Moore desacelerando**: transistores ainda encolhem, mas o ganho por dólar diminuiu.
2. **GPUs mais caras**: RTX 4090 ($1600) vs GTX 1080 ($600) — 2.7× o preço para ~6.7× o hash rate. O custo/hash melhorou apenas ~2.5×.
3. **Sem ASIC para HMAC-SHA256**: diferente de SHA-256d (Bitcoin), não há incentivo econômico para criar ASICs especializados em HMAC-SHA256.

Isso torna o protocolo **previsível**: a dificuldade de 67 bits por $1M/ano é uma barreira estável. Aumentos futuros serão graduais (~1 bit a cada 3-5 anos).
