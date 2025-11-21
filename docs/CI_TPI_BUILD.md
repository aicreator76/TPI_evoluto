# Build TPI (stub) – Collegamento CESARE ↔ GitHub Actions

## 1. Come creare un tag con CESARE_TPI_CI_BRIDGE.ps1

Per lanciare una build DEMO TPI che attiva il workflow **Build TPI (stub)** su GitHub:

Comandi da usare:

- Set-Location "E:\CLONAZIONE\scripts\CESARE"
- .\CESARE_TPI_CI_BRIDGE.ps1 -Version "vTEST-CI-BRIDGE-001"

Lo script:

- crea un tag 	pi-vTEST-CI-BRIDGE-001 nel repo TPI_evoluto;
- push-a il tag su GitHub;
- allinea la versione usata da CESARE con quella vista dalla CI.

## 2. Cosa succede in GitHub Actions (workflow Build TPI stub)

Quando arriva un tag 	pi-v* su GitHub:

- si attiva il workflow .github/workflows/build-tpi.yml;
- vengono eseguiti gli script:
  - ci/CESARE_BUILD_TPI_WIN.ps1
  - ci/CESARE_BUILD_TPI_APK.ps1;
- la run produce solo file **STUB** (nessun .exe o .apk reale) sotto:
  - E:\CLONAZIONE\RELEASE_TPI\YYYY-MM-DD\WIN\...-WIN-STUB.txt
  - E:\CLONAZIONE\RELEASE_TPI\YYYY-MM-DD\APK\...-ANDROID-STUB.txt.

Per vedere la run:

1. Apri la tab **Actions** del repo TPI_evoluto;
2. Seleziona il workflow **Build TPI (stub)**;
3. Apri la run associata al tag 	pi-vTEST-CI-BRIDGE-001.

## 3. Limitazioni attuali (stato DEMO)

- Non vengono generati eseguibili Windows .exe reali;
- Non vengono generati pacchetti Android .apk installabili;
- La pipeline serve solo per:
  - accendere la CI,
  - verificare il collegamento CESARE ↔ GitHub,
  - testare il flusso con file STUB;
- Le build reali verranno documentate in una sezione separata quando saranno pronte e testate.
