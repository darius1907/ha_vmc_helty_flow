# VMC Helty Flow Integration

[![hacs][hacsbadge]][hacs]
[![GitHub Release][releases-shield]][releases]

Integrazione completa per sistemi di Ventilazione Meccanica Controllata (VMC) Helty Flow con Home Assistant.

## ✨ Funzionalità Principali

### 🔍 Scoperta Automatica

- Scansione intelligente della rete locale
- Configurazione guidata passo-passo
- Supporto multi-dispositivo

### 🎛️ Controllo Completo

- Controllo velocità ventola (4 livelli)
- Modalità operative: Normal, Night, Hyperventilation, Free Cooling
- Controllo LED pannello e sensori
- Controlli luci con timer automatico

### 📊 Monitoraggio Avanzato

- **Sensori Ambientali**: Temperatura interna/esterna, umidità, CO2, VOC
- **Sensori Tecnici**: Portata aria, ore filtro, stato dispositivo
- **Analytics Avanzati**: Punto di rugiada, indice comfort, ricambi aria
- **Informazioni Rete**: IP dispositivo, ultima comunicazione

### 🎨 Lovelace Card Integrata

- Card personalizzata per controllo e monitoraggio
- Editor visuale integrato
- Temi personalizzabili e layout responsive
- Componenti Home Assistant nativi

## 🚀 Installazione

1. **Installa via HACS**:
   - Aggiungi questo repository in HACS
   - Cerca "VMC Helty Flow"
   - Installa e riavvia Home Assistant

2. **Configura l'integrazione**:
   - Vai in Impostazioni → Dispositivi e Servizi
   - Aggiungi integrazione "VMC Helty Flow"
   - Segui la configurazione guidata

3. **Aggiungi la card** (opzionale):
   - Copia i file da `www/vmc-helty-card/` in `www/`
   - Aggiungi la risorsa Lovelace
   - Configura la card nel dashboard

## 🔧 Configurazione

L'integrazione supporta:

- **Scansione di rete personalizzabile** (subnet, porte, timeout)
- **Sensori opzionali** configurabili individualmente
- **Calcoli di comfort** con volume stanza personalizzabile
- **Modalità debug** per troubleshooting avanzato

## 📚 Documentazione

- [Guida Completa](https://github.com/darius1907/ha_vmc_helty_flow/blob/main/README.md)
- [Installation Guide](https://github.com/darius1907/ha_vmc_helty_flow#-installazione-rapida)
- [Card Configuration](https://github.com/darius1907/ha_vmc_helty_flow#-lovelace-card)
- [Troubleshooting](https://github.com/darius1907/ha_vmc_helty_flow#-risoluzione-problemi)

## 🐛 Segnalazione Bug

Segnala problemi su [GitHub Issues](https://github.com/darius1907/ha_vmc_helty_flow/issues)

---

**Sviluppato con ❤️ per la community Home Assistant**

[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/dpezzoli/ha_vmc_helty_flow.svg?style=for-the-badge
[releases]: https://github.com/dpezzoli/ha_vmc_helty_flow/releases
