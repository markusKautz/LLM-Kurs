FROM python:3.12-slim

# PyTorch in der Variante ohne Grafikkarten-Unterstützung.
# Sie ist deutlich kleiner und reicht für die Modelle im Kurs.
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.14.1

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN useradd --create-home --shell /bin/bash lehrling
USER lehrling

# Die Notebooks werden beim Start von außen eingebunden,
# damit eure Arbeit auf eurem Rechner gespeichert bleibt.
WORKDIR /kurs/notebooks
EXPOSE 8888

# Wird nur verwendet, wenn der Container ohne VS Code gestartet wird
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", \
     "--IdentityProvider.token=", "--ServerApp.root_dir=/kurs/notebooks"]
