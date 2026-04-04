
# 🏥 CareSurge AI (Platformă Geospațială de Triaj Predictiv și Simulare la Cerere)

**Proiect dezvoltat pentru Hackathon-ul „Prove It” - Proba de 24h (Sponsor: Tremend / Publicis Sapient)**

---

## 📌 1. Rezumatul Proiectului (Executive Summary)
**CareSurge AI** este o platformă HealthTech centralizată, dezvoltată pentru managementul proactiv al resurselor spitalicești. Printr-o arhitectură On-Demand, platforma permite managerilor medicali să selecteze orice spital din rețea, moment în care sistemul deduce automat locația geografică, extrage datele de context local (vreme, evenimente) și combină Machine Learning-ul cu Agentic AI (LLM) pentru a genera instantaneu predicții de risc pe departamente și planuri de acțiune explicate.

---

## 🎯 2. Problema Medicală & Impactul
* **Problema:** Un spital județean de la munte (ex: Brașov) se confruntă cu cu totul alte tipare de crize (ex: avalanșe, polei extrem) față de un spital de pe litoral (ex: Constanța - insolații, festivaluri de vară). Un sistem predictiv rigid, care nu ține cont de contextul geospațial, este inutil.
* **Soluția CareSurge AI:** Un sistem flexibil, la cerere. AI-ul înțelege contextul local al fiecărui spital și oferă medicilor puterea de a interoga datele și de a rula simulări doar atunci când au nevoie, eliminând "zgomotul" alertelor automate irelevante.

---

## ✨ 3. Funcționalități Core (Arhitectură On-Demand & LLM)

### 1. Profilare Geospațială și Predicție la Cerere (On-Demand Routing)
* **Cum funcționează:** Utilizatorul deschide aplicația și selectează din meniu instituția (ex: *Spitalul Clinic Județean de Urgență Cluj*). 
* **Logica de Backend:** Sistemul deduce instantaneu regiunea de activitate (coordonatele GPS ale orașului Cluj) și trage prin API datele meteo stricte pentru acea zonă.
* **Output LLM:** La apăsarea butonului **[Generează Raport de Risc]**, datele meteo locale și istoricul acelui spital trec prin modelul ML, iar LLM-ul oferă un raport punctual pe departamente. *(Ex: "Pentru locația Cluj, anticipăm un vârf la Toxicologie diseară din cauza unui festival major. Restul secțiilor sunt în parametri normali.")*

### 2. Explicații la Cerere (AI Explainability & Deep Dive)
* **Cum funcționează:** Sub fiecare estimare generată, utilizatorul are opțiunea de a cere justificarea deciziei. 
* **Magia LLM:** Modelul nu oferă doar procente reci, ci „traduce” factorii matematici în limbaj uman: *"Am estimat o creștere de 45% la Ortopedie la Spitalul Sf. Spiridon Iași deoarece, conform Open-Meteo, mâine la ora 06:00 va ploua la temperaturi de -2°C (ploaie înghețată/polei), un tipar care în istoricul nostru a generat mereu suprasolicitarea acestei secții."*

### 3. Simulatorul de Scenarii „What-If” (Crisis Stress-Test)
* **Cum funcționează:** Managerul spitalului selectat poate interoga sistemul cu scenarii ipotetice de dezastru.
* **Magia LLM + ML:** Utilizatorul scrie: *"Ce s-ar întâmpla cu resursele noastre dacă mâine ar lovi un val de caniculă de 40°C în oraș?"*. LLM-ul preia parametrii din text, forțează algoritmul ML (`Prophet`) să recalculeze predicția pentru acel spital specific și emite un plan de contingență.

---

## ⚙️ 4. Arhitectura Tehnică & Fluxul de Date

* **Pasul 1 (Mapare Geografică & Ingestie la Cerere):**
  * Un dicționar/config de bază care mapează `Spital -> Coordonate GPS`.
  * Apel dinamic către `Open-Meteo API` bazat pe locația dedusă a spitalului selectat.
* **Pasul 2 (Procesare ML On-Demand):**
  * Filtrarea fișierului CSV (datele istorice) pentru a potrivi spitalul și departamentul.
  * Rularea algoritmului `Prophet` pe loc, la apăsarea butonului.
* **Pasul 3 (AI Generativ / LLM Engine):**
  * `OpenAI API / Gemini` structurează rezultatele matematice în planuri de acțiune și interpretează scenariile „What-If” prin extragere de entități.
* **Pasul 4 (Interfață Streamlit):**
  * Un UI curat, bazat pe selectoare (Dropdowns) pentru Spital/Secție, butoane de execuție ("Rublează Predicția") și zone de chat pentru simulări.

---

## 👥 5. Echipa și Distribuția Rolurilor (24h Sprint)

* 🛠️ **Data Engineer (Geospatial & APIs):** Creează dicționarul de mapare a spitalelor (`hospital_locations.json`). Configurează API-ul Meteo să primească dinamic latitudinea/longitudinea în funcție de spitalul selectat. Formatează datele pentru a fi trimise către ML.
* 🧠 **AI & ML Engineer (Core Predictiv):** Conectează modelul Prophet la pipeline-ul on-demand. Scrie prompturile avansate care obligă LLM-ul să explice logic (Deep-Dive) și să extragă parametrii din textul "What-if".
* 💻 **Frontend & Product Lead:** Asamblează dashboard-ul în `Streamlit`. Se asigură că UX-ul este impecabil (utilizatorul alege locația -> apasă buton -> primește analiza). Realizează "pitch-ul" final.

---

## 📊 6. Structura Prezentării Finale (Pitch Deck)

1. **Problema:** Riscul medical variază enorm de la o regiune la alta. Nu putem trata un spital de munte la fel ca unul de câmpie.
2. **Soluția:** CareSurge AI – Platforma geospațială la cerere. 
3. **Demo Live (Momentul de Glorie):** * Se selectează Spitalul Județean Constanța -> AI-ul trage date meteo de pe litoral -> Arată riscurile.
   * Se schimbă pe Spitalul Județean Brașov -> AI-ul trage date meteo de munte -> Riscurile se schimbă complet.
   * Se face un Deep-Dive pentru a demonstra explicabilitatea și se rulează o simulare What-If scurtă.
4. **Arhitectura Tehnică:** Prezentarea modului în care funcționează rutarea dinamică a datelor și simbioza ML + LLM.
5. **Viziunea de Viitor:** O hartă interactivă a României unde Ministerul Sănătății poate vedea riscurile pe toate spitalele simultan.