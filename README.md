ssh connection command
ssh -i .ssh/english-conversation-for-you-backend.pem ubuntu@13.112.150.63
scp -i .ssh/english-conversation-for-you-backend.pem app.py requirements.txt ubuntu@13.112.150.63:/home/ubuntu/english-conversation-for-you-backend
wsl ec2 ubuntu initialize method
sudo apt update
sudo apt upgrade
sudo apt install python-pip

https://www.twilio.com/blog/deploy-flask-python-app-aws-jp
tmux attach -t english-conversation-for-you-backend


http://ec2-13-112-150-63.ap-northeast-1.compute.amazonaws.com:8080/