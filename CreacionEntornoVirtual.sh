#download postgreSQL
sudo apt update
sudo apt install postgresql-client

#creation for the virtual enviroment
touch requierements.txt
mkdir EntornoVirtual
cd EntornoVirtual
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
echo "export PATH="~/miniconda3/bin:$PATH"" >> ~/.bashrc
conda create --name myenv python=3.9
conda activate myenv
cd ..
echo "fastapi" > requierements.txt
echo "uvicorn" >> requierements.txt
echo "sqlalchemy" >> requierements.txt
echo "asyncpg" >> requierements.txt
echo "psycopg2-binary" >> requierements.txt
echo "alembic" >> requierements.txt
echo "pydantic" >> requierements.txt
echo "pandas" >> requierements.txt
echo "boto3" >> requierements.txt
echo "botocore" >> requierements.txt
pip install -r requierements.txt
