# Basis-Image
FROM gvenzl/oracle-xe:21.3.0

# Setze das Standardpasswort für den Oracle-User
ENV ORACLE_PASSWORD=oracle

# Optional: Setze weitere sinnvolle Umgebungsvariablen
# ENV ORACLE_DATABASE=XE
# ENV ORACLE_USER=system
# ENV APP_USER_PASSWORD=orcale

# Kopiere deine PL/SQL- oder SQL-Init-Skripte ins passende Verzeichnis
# Diese werden beim ersten Start automatisch ausgeführt
COPY ./backend-plsql /docker-entrypoint-initdb.d

# Exponiere die Standardports
EXPOSE 1521 5500

# Starte den Oracle-Datenbankdienst
CMD ["oracle-xe"]
