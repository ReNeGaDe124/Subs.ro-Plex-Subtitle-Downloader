<p align="center">
  <img src="https://github.com/user-attachments/assets/85c9a86d-de41-48da-a4a1-e16a0c6e04ac" alt="logo">
</p>

# Subs.ro Plex Subtitle Downloader - Add-on și Integrare pentru Home Assistant

Descarcă automat subtitrări în limba română de pe Subs.ro pentru Plex Media Server. (Home Assistant)

## ✨ Funcționalități
  - Descărcare automată a subtitrării pentru fișiere video nou importate în Plex Media Server (🧩)
  - Logică robustă de alegere a subtitrării pentru a selecta o versiune cât mai potrivită pentru fișierul video în cauză și pentru a minimiza cât mai mult posibil apelarea API-ului Subs.ro (🧩)
  - Convertire automată a subtitrărilor în format "UTF8 with BOM" pentru o compatibilitate sporită (🧩)
  - Redenumirea subtitrărilor pentru a include extensia ".ro.srt" și plasarea în folderul fișierului video pentru preluarea în mod automat și clar de către Plex Media Server (🧩)
  - Rulare activități la o oră programată:
      - Descărcare subtitrări pentru toate fișierele video ce nu au o subtitrare asociată (🧩)
      - Curățare subtitrări orfane ce nu mai au un fișier video asociat (🧩)
  - Rulare activități în mod manual:
      - Descărcare subtitrări pentru toate fișierele video ce nu au o subtitrare asociată (🧩+🔗)
      - Curățare subtitrări orfane ce nu mai au un fișier video asociat (🧩+🔗)
      - Descărcare subtitrare pentru cel mai recent fișier video importat în Plex Media Server (🧩+🔗)
      - Căutare și descărcare de subtitrări pentru fișierele video din librăria Plex Media Server pe baza cuvintelor cheie introduse în câmpul de căutare (🧩+🔗)
      - Căutare și ștergere de subtitrări pentru fișierele video din librăria Plex Media Server pe baza cuvintelor cheie introduse în câmpul de căutare (🧩+🔗)
  - Entitate de tip senzor ce permite vizualizarea statusului add-on-ului Subs.ro Plex Subtitle Downloader și acces facil la vizualizarea logului ultimei acțiuni făcute de către acesta (🧩+🔗)

(🧩) = funcționalitate ce necesită doar instalarea add-on-ului<br>
(🧩+🔗) = funcționalitate ce necesită atât instalarea add-on-ului cât și a integrării

## 🛠️ Instalare

### 🧩 Add-on
  1. Adaugă acest repository în instanța ta de Home Assistant: <br><br>[![https://github.com/ReNeGaDe124/Subs.ro-Plex-Subtitle-Downloader](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/ReNeGaDe124/Subs.ro-Plex-Subtitle-Downloader)<br>
  2. Caută add-on-ul `Subs.ro Plex Subtitle Downloader` și instalează-l.

### 🔗 Integrare

#### Automat prin HACS
  1. Adaugă acest repository în instanța ta de Home Assistant: <br><br>[![https://github.com/ReNeGaDe124/Subs.ro-Plex-Subtitle-Downloader](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ReNeGaDe124&repository=Subs.ro-Plex-Subtitle-Downloader&category=Integration)
  2. Caută integrarea `Subs.ro Plex Subtitle Downloader` și instalează-o.
  3. Restartează Home Assistant.
  4. În secțiunea `Devices & services` din Home Assistant, apasă pe butonul `+ Add integration`.
  5. Caută și alege din listă `Subs.ro Plex Subtitle Downloader`.

#### Manual
  1. Descarcă fișierele din acest repository.
  2. Copiază folderul `custom_components/subsro` în directorul `custom_components` din Home Assistant.
  3. Restartează Home Assistant.
  4. În secțiunea `Devices & services` din Home Assistant, apasă pe butonul `+ Add integration`.
  5. Caută și alege din listă `Subs.ro Plex Subtitle Downloader`.

## ⚙️ Configurare

### 🧩 Add-on

<p align="center">
  <img src="https://github.com/user-attachments/assets/5de500b1-58ed-45f2-bda0-eb24c51afb8e" width="250" />
</p>

| Opțiune | Tip | Implicit | Descriere |
|--------|------|---------|-------------|
| <p align="center">`plex_url`</p> | <p align="center">str</p> | `http://localhost:32400` | Linkul către serverul Plex Media Server. |
| <p align="center">`plex_token`</p> | <p align="center">str</p> | | Token de autentificare Plex Media Server - X-Plex-Token (vezi [aici](https://github.com/ReNeGaDe124/Subs.ro-Plex-Subtitle-Downloader?tab=readme-ov-file#-x-plex-token) cum să îl obții). |
| <p align="center">`subsro_api_key`</p> | <p align="center">str</p> | | Token de autentificare API Subs.ro (vezi [aici](https://github.com/ReNeGaDe124/Subs.ro-Plex-Subtitle-Downloader?tab=readme-ov-file#-api_token_subsro) cum să îl obții). |
| <p align="center">`webhook_secret`</p> | <p align="center">password?</p> | | Parola ce va fi folosită pentru interconectarea dintre Add-on și Integrare (dacă nu se dorește folosirea Integrării câmpul poate rămâne gol). |
| <p align="center">`scheduled_download`</p> | <p align="center">bool</p> | <p align="center">`ON`</p> | Activare/Dezactivare a funcției de descărcare subtitrări pentru toate fișierele video ce nu au o subtitrare asociată. |
| <p align="center">`scheduled_cleanup`</p> | <p align="center">bool</p> | <p align="center">`ON`</p> | Activare/Dezactivare a funcției de curățare subtitrări orfane ce nu mai au un fișier video asociat. |
| <p align="center">`scan_time`</p> | <p align="center">str</p> | <p align="center">`03:00`</p> | Ora la care vor rula funcțiile `scheduled_download` și/sau `scheduled_cleanup`. |
| <p align="center">`debug_log`</p> | <p align="center">str</p> | <p align="center">`OFF`</p> | Activare/Dezactivare funcție logare detaliată. |

Mențiune: Add-on-ul funcționează pe portul **8999**. Acesta trebuie să nu fie folosit de alt add-on sau aplicație.

### 🔗 Integrare

<p align="center">
  <img src="https://github.com/user-attachments/assets/cba9f6d7-d273-46c2-a28a-a9178b6ed4c2" width="300" />
</p>

| Opțiune | Tip | Implicit | Descriere |
|--------|------|---------|-------------|
| <p align="center">`url`</p> | <p align="center">str</p> | `http://localhost:8999` | Linkul către Add-on-ul Subs.ro Plex Subtitle Downloader. (în mod normal nu trebuie schimbat) |
| <p align="center">`secret`</p> | <p align="center">str</p> | | Parola folosită în câmpul `webhook_secret` din Add-on. |

## ▶️ Utilizare Integrare

<p align="center">
  <img src="https://github.com/user-attachments/assets/b7277e41-2f55-439a-a331-c43bdc1bfb87" width="300" />
</p>

| Opțiune | Metoda de activare | Descriere |
|--------|-------------|----------|
| <p align="center">`Cleanup Orphaned Subtitles`</p> | <p align="center">Apăsare pe buton</p> | Activare manuală a funcției de curățare subtitrări orfane ce nu mai au un fișier video asociat. |
| <p align="center">`Download for Latest Video`</p> | <p align="center">Apăsare pe buton</p> | Activare manuală a funcției de descărcare subtitrare pentru cel mai recent fișier video importat în Plex Media Server. |
| <p align="center">`Download Missing Subtitles`</p> | <p align="center">Apăsare pe buton</p> | Activare manuală a funcției de descărcare subtitrări pentru toate fișierele video ce nu au o subtitrare asociată. |
| <p align="center">`Search & Download Subtitles`</p> | <p align="center">Introducere text în câmpul de căutare</p> | Activare manuală a funcției de căutare și descărcare de subtitrări pentru fișierele video din librăria Plex Media Server pe baza cuvintelor cheie introduse în câmpul de căutare. |
| <p align="center">`Search & Delete Subtitles`</p> | <p align="center">Introducere text în câmpul de căutare</p> | Activare manuală a funcției de căutare și ștergere de subtitrări pentru fișierele video din librăria Plex Media Server pe baza cuvintelor cheie introduse în câmpul de căutare. |
| <p align="center">`Status`</p> |  | Entitate de tip senzor ce permite vizualizarea statusului add-on-ului Subs.ro Plex Subtitle Downloader și acces facil la vizualizarea logului ultimei acțiuni făcute de către acesta. **(Stări posibile: Offline, Booting, Idle, Processing)** |

### 📋 Exemplu de card pentru Dashboard

```yaml
type: entities
entities:
  - entity: button.subs_ro_plex_subtitle_downloader_cleanup_orphaned_subtitles
    name: Cleanup Orphaned Subtitles
  - entity: button.subs_ro_plex_subtitle_downloader_download_for_latest_video
    name: Download for Latest Video
  - entity: button.subs_ro_plex_subtitle_downloader_download_missing_subtitles
    name: Download Missing Subtitles
  - entity: text.subs_ro_plex_subtitle_downloader_search_download_subtitles
    name: Search & Download Subtitles
  - entity: text.subs_ro_plex_subtitle_downloader_search_delete_subtitles
    name: Search & Delete Subtitles
  - entity: sensor.subs_ro_plex_subtitle_downloader_status
    name: Status
title: Subs.ro Plex Subtitle Downloader
```

### 🟢🟡🔴 Exemple de posibile rezultate în secțiunea `Attributes` a senzorului `Status`:

<p align="center">
  <img src="https://github.com/user-attachments/assets/555599f3-0125-4de3-b7ef-84fd63a6d49e" width="200" />
  <img src="https://github.com/user-attachments/assets/1ed95ae3-2df2-4fb1-bbbd-1446cfa9f6d7" width="200" />
  <img src="https://github.com/user-attachments/assets/a99dfce8-80cc-41f5-8352-e230caff852d" width="200" />
  <img src="https://github.com/user-attachments/assets/8aaf0139-69b5-450f-a99b-acd4ddd8b4f2" width="200" />
</p>

## 📦 Dependențe

### 🎬 X-Plex-Token

  1. Conectează-te pe serverul tău Plex Media Server.
  2. Apasă pe butonul `⋮` pe unul din obiectele din librărie și apoi pe opțiunea `Get Info`.

<p align="center">
  <img width="338" alt="get-info" src="https://github.com/user-attachments/assets/4d70b189-c404-4439-8e20-14833bc6e6bb" />
</p>

  3. Apasă pe butonul `View XML`.

<p align="center">
<img width="500" alt="view-xml" src="https://github.com/user-attachments/assets/e5ee4523-5657-460d-bb61-c01a9cddd7ca" />
</p>

  4. Copiază din bara de adresă a paginii care se deschide valoarea de la sfârșitul linkului, de după `X-Plex-Token=`.

<p align="center">
<img width="693" height="108" alt="x-plex-token" src="https://github.com/user-attachments/assets/79835b17-f494-4ee8-bdba-3bb3e36e3982" />
</p>

  5. Pune valoarea copiată în câmpul `plex_token` din Add-on.

### 💬 API Token Subs.ro

  1. Creează-ți cont pe [Subs.ro](https://subs.ro/).
  2. Loghează-te și accesează [pagina de profil](https://subs.ro/utilizator/profil).
  3. Mergi la secțiunea `Acces API` și apasă pe butonul `Generează o cheie API`.

<p align="center">
<img width="300" alt="subsro-generate-api-key" src="https://github.com/user-attachments/assets/7f744f0c-b054-4ff2-b4ed-c7ad71791dc7" />
</p>

  4. Copiază valoarea din secțiunea `Cheia dumneavoastră API`.

<p align="center">
<img width="350" alt="subsro-copy-api-key" src="https://github.com/user-attachments/assets/9e8c7940-2c7a-4ce6-acb0-6cab32a63279" />
</p>

  5. Pune valoarea copiată în câmpul `subsro_api_key` din Add-on.

## 📜 Note de final ❤️
  - Mulțumiri echipei Subs.ro pentru activarea API-ului! Fără acesta proiectul de față nu ar fi fost posibil.  Mulțumiri de asemenea și tuturor traducătorilor! Logoul și subtitrările aparțin Subs.ro.🙏
  - Cod sursă al proiectului realizat în totalitate folosind Google Gemini. 🤖
  - Dacă aveți idei de îmbunătățire sau doriți să semnalați probleme cu acest proiect, le aștept cu plăcere. 🤗
  - Acesta este un proiect făcut din pasiune dar dacă îți place, îl găsești folositor și vrei să susții dezvoltarea lui pe viitor, dar și munca depusă până acum, o poți face printr-o contribuție scanând codul QR generat de Revolut de mai jos. Vă mulțumesc! 🫶

<p align="center">
<img width="250" alt="revolut" src="https://github.com/user-attachments/assets/279c753c-e420-47fa-95a7-ed6c45c263e5" />
</p>
