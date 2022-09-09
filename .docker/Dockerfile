FROM python:3.8

WORKDIR /app

# Install pip requirements
COPY requirements.dev.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.dev.txt

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["tail", "-f", "/dev/null"]
