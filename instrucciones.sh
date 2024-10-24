sh instalacionDocker.sh
sh CreacionEntornoVirtual.sh
sh agregarCsvDocker.sh
uvicorn main:app --host 0.0.0.0 --port 8000
#sh validationEndPoints.sh
