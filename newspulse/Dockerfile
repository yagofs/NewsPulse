FROM python:3.14-slim

WORKDIR /opt/newspulse
COPY backend/requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY frontend ./frontend

EXPOSE 4173
CMD ["python", "backend/server.py"]
