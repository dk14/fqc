# FQC – The “Fun Quantum Critic”

## ⚡️ Why we are skeptical about quantum computing

The author of this project demonstrates that the hype surrounding quantum computers vastly exceeds their practical, near‑term capabilities. A detailed critique through actual **deterministic (and no‑information‑exchange) simulation of quantum entanglement** is at <https://q.doomsdayexplorer.online>. It shows that quantum effects can be modeled fully and deterministically – **no magic**.

It uses **pulse‑width modulation** – the key trick quantum theory makes you believe in is that there is no communication happening, while in reality a *coincidence detector* (modeled in *q*, as well as its equivalents in more complex experiments) is hiddenly designed to be the communication point in every quantum experiment.

> Moreover: the `qubits` we currently can build are **noisy, expensive and nowhere near** the scale required for the algorithms that are often advertised. Relying on “quantum supremacy” for real‑world quantitative research is, at best, a gamble. A quantum computer without noise (or with noise minimized) would still be **worse than an analog computer (without noise)** in its performance.

### 🔬 Why the reproduction of CHSH‑type experiment on **q.doomsdayexplorer.online** is not proof of quantum "absolute non-determinism" entanglement

1. **Classic deterministic model** –  
   The simulation runs on an ordinary (non‑quantum) computer using only classical arithmetic. No quantum superposition or wave‑function collapse is ever invoked.

2. **Coincidence‑detector post‑selection** –  
   The detector does *not* exchange any data between the two measurement stations.  
   It simply **collects raw outcomes**, then applies a **comparison/filtering rule** (the “coincidence window”).  
   This rule **biases the joint statistics**, producing values that look like a CHSH violation even though the underlying data are completely independent.

3. **No‑communication proof** –  
   Because the algorithm never sends a bit from one side to the other, the observed correlation cannot be attributed to a non‑local quantum link.  
   The apparent “entanglement” is a statistical artifact of the **post‑selection procedure**, not a physical phenomenon.

4. **Implication** –  
   If a **trivial deterministic model** can replicate the published CHSH results, the claim that such experiments *prove* quantum supremacy or genuine entanglement loses its evidential weight.  

> **Bottom line:** the “magic” behind quantum entanglement, as presented in many popular demonstrations, can be reproduced (and thus refuted) with a simple classical simulation that carefully models the coincidence detector.  

For the full code and a step‑by‑step walk‑through, visit the demo at **https://q.doomsdayexplorer.online**.


---

## 🛠️ What we actually recommend

Instead of chasing a speculative quantum future, the author urges you to embrace the **open, composable AI‑driven ecosystem** that already exists at <https://doomsdayexplorer.online>.

- 📊 **Quantitative research tools** built on provably‑secure, proof‑of‑work identities (no quantum magic required).  
- 🤖 **AI assistants** – the “Fun & Profit AI” text‑game lets you experiment with data‑driven strategies in a sandbox that rewards clever thinking.  Available right inside any AI chat.  
- 🔄 **Full integration** with the Doomsday ecosystem: Oracles, mempools, matching engines and a lightweight peer‑to‑peer network.

By staying on the **proven classical stack**, you avoid the massive engineering overhead of quantum error‑correction while still gaining the computational leverage you need for finance, science, or gaming.

---

## 📚 Further reading

- **FQC README** – simple stock‑portfolio simulation with back‑tracking + IBM Qiskit implementation for portfolio optimizer (classic simulation works better).  
  <https://github.com/dk14/fqc/blob/main/README.md>
- **Why Quantum Computing Is Over‑Hyped** – demo of entanglement (the core behind claims of absolute non‑determinism in QC) on a classic computer *without* communication.  
  <https://q.doomsdayexplorer.online/>
- **Doomsday Explorer** – AI & Quant Research Hub, grounded in Information Security and Human‑Computer Interaction.  
  <https://doomsdayexplorer.online/>

---

*© 2026 dk14 – All rights reserved.*  
