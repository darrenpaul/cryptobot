Create Venv
python3 -m venv venv

Run on EC2 machine
./run_script

List process on EC2 machine
ps -ef | grep python

Kill process on EC2 machine
kill process_id

Getting onto ec2 machine
ssh pi@192.168.0.101