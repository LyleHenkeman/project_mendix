#!/bin/bash -x

REGION=$(curl 169.254.169.254/latest/meta-data/placement/availability-zone/ ｜ sed 's/[a-z]$//')

yum update -y

yum install ruby wget

yum install httpd

cd /home/ec2-user

wget https://aws-codedeploy-eu-central-1.s3.amazonaws.com/latest/install

chmod +x ./install

./install auto