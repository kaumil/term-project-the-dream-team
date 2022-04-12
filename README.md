[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-f059dc9a6f8d3a56e377f745f24479a46679e63a5d9fe6f495e02850cd0d8118.svg)](https://classroom.github.com/online_ide?assignment_repo_id=6957561&assignment_repo_type=AssignmentRepo)
# Online NFT Marketplace

Final Project for CMPT 756 Distributed & Cloud Systems.

## About
This application is a marketplace for the sale and purchase of Non-Fungible Tokens (NFTs). The application utilizes a highly decoupled microservice architecture with five core services, each of which are Flask applications. Load testing, metric recording, and dashboarding is implemented for scalability analysis. Continuous Integration and Delivery are provided by workflows in GitHub Actions.


## Technologies Used
- Python
- Flask
- Prometheus
- Grafana
- Gatling
- Docker
- Amazon EC2, EKS, and DynamoDB


## System Design
![image](https://user-images.githubusercontent.com/52950086/162638350-96c1dca9-e295-4ab3-b17c-00da36ba5b46.png)

## Setup and Installation

- After cloning the repository, access the tool container via the command: `tools/shell.sh`
- Setup the templates using the command: `make -f k8s-tpl.mak templates`
- Provision the EKS cluster using the command: `make -f eks.mak start`
- Install Istio and configure the other services using the command `tools/setup.sh`
- The cluster is now setup. Access Grafana via the command `make -f k8s.mak grafana-url`
- Prometheus can be accessed using the command `make -f k8s.mak prometheus-url`
- Kiali can be accessed using the command `make -f k8s.mak kiali-url`
- Gatling tests can be performed in the following manner:
    - To perform gatling user test scenario use the command `tools/gatling-user-test.sh $(NUMBER_OF_USERS)`
    - To perform gatling image test scenario use the command `tools/gatling-user-test.sh $(NUMBER_OF_USERS)`
    - To perform gatling transaction test scenario use the command `tools/gatling-user-test.sh $(NUMBER_OF_USERS)`
- The K9s service can be accessed via the command `k9s`

