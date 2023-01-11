FROM gitpod/workspace-python-3.11:latest

# Install & configure Doppler CLI
RUN (curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh || wget -t 3 -qO- https://cli.doppler.com/install.sh) | sudo sh
# Install & configure ngrok
RUN wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz && tar zxvf ngrok-v3-stable-linux-amd64.tgz && rm -f ./ngrok-v3-stable-linux-amd64.tgz