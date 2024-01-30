# REAL-UP: Urban Perceptions From LBSNs Helping Moving Real-Estate Market to the Next Level

![Python Version](https://img.shields.io/badge/python-v3.7-blue)



REAL-UP is an interactive tool designed to enrich real-estate marketplaces. In addition to information commonly provided by such applications, e.g., rent price, REAL-UP also provides subjective neighborhood information based on Location-Based Social Network messages. This novel tool helps to represent complex users’ subjective perceptions of urban areas, easing the process of finding the best accommodation.



Please, cite the paper if you use or discuss REAL-UP's code or data in your work:

```shell
@inproceedings{santos2024real,
  title={REAL-UP: Urban Perceptions From LBSNs Helping Moving Real-Estate Market to the Next Level},
  author={Santos, Frances A and Silva, Thiago H and Villas, Leandro A},
  booktitle={},
  pages={},
  year={2024},
  organization={}
}
```

## Clone the project and make some tests

1. Install Git and Clone the project

```sh
sudo apt install git
git clone https://github.com/francessantos/real-up.git
```

2. Install the dependencies and run the server

```sh
cd real-up/
pip install -r requirements.txt
python realup_server.py
```

3. Access REAL-UP's homepage in your web browser: http://0.0.0.0:8080

## Docker

1. Install Docker

```sh
sudo apt-get install ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo   "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

2. Creating a Docker container for REAL-UP server and run it

```sh
sudo docker image build . --tag realup/server && sudo docker container run --restart unless-stopped -d -e PORT=81 -p 8080:8080 --network host --name realup-server --shm-size 1g realup/server
```

3. Access REAL-UP's homepage in your web browser: http://0.0.0.0:81

4. See the status of realup-server container

```sh
sudo docker container ls -a
```

5. Install pytest and run the tests

```sh
sudo pip install pytest
python -m pytest tests/test_realup.py
```

6. See the logs of realup-server container

```sh
sudo docker logs realup-server
```

7. Stop and remove realup-server container

```sh
sudo docker stop realup-server && sudo docker rm realup-server
```
