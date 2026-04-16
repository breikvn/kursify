# kursify

Aktueller Buchungsfluss:

- Bei der Kursauswahl wird zunaechst eine `PENDING`-Reservierung mit 24 Stunden Frist angelegt.
- Der Benutzer erhaelt eine Bestaetigungs-E-Mail an die im Employee-Datensatz hinterlegte Adresse.
- Erst nach Klick auf den Link `/api/enrollments/confirm?token=...` wird die Teilnahme auf `CONFIRMED` gesetzt.
- Ist die Frist abgelaufen, wird der reservierte Platz automatisch wieder freigegeben, sobald Kursdaten erneut abgefragt oder der Link geoeffnet wird.

Ollama-Integration fuer Mailtexte:

- Der Mailtext kann optional von Ollama erzeugt werden.
- Dafuer im Django-Service `OLLAMA_EMAIL_MODEL` setzen, zum Beispiel `llama3.2`.
- Ohne gesetztes Modell oder bei Ollama-Fehlern faellt das Backend automatisch auf einen statischen deutschen Mailtext zurueck.

E-Mail-Versand:

- Der Docker-Stack ist jetzt auf SMTP ausgelegt. Lege im Projektroot eine `.env` auf Basis von [.env.example](/Users/kevinbreinert/Documents/GitHub/kursify/.env.example:1) an.
- Fuer echte E-Mails muessen mindestens `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` und `DEFAULT_FROM_EMAIL` gesetzt sein.
- Danach den Django-Container neu starten, damit Buchungsbestaetigungen tatsaechlich an die hinterlegte Benutzer-E-Mail versendet werden.
