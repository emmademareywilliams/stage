.PHONY: install

user := $(shell id -u -n)

service_dir := /etc/systemd/system

exe_dir := /usr/local/bin/bios
log_dir := /var/log/bios
conf_dir := /etc/bios
name := ota2tcp

here := $(shell pwd)
exe_name := $(here)/$(name).py

install:
	@sudo chmod +x $(exe_name)
	@echo "creating conf dir and populating with a conf file"
	@sudo mkdir -p $(conf_dir)
	@sudo cp enless.conf $(conf_dir)/$(name).conf
	@sudo chmod 666 $(conf_dir)/$(name).conf
	@echo "creating the log folder/file"
	@sudo mkdir -p -m 775 $(log_dir)
	@sudo chgrp -R $(user) $(log_dir)
	@echo "creation du fichier de service"
	@printf "[Unit]\n" > ota2tcp.service
	@printf "Description=Over The Air Packet Management to tcp socket\n" >> ota2tcp.service
	@printf "After=network.target redis.service mosquitto.service\n" >> ota2tcp.service
	@printf "\n" >> ota2tcp.service
	@printf "[Service]\n" >> ota2tcp.service
	@printf "User=$(user)\n" >> ota2tcp.service
	@printf "ExecStart=$(exe_dir)/$(name).py --conf=$(conf_dir)/$(name).conf --log=$(log_dir)/$(name).log\n" >> ota2tcp.service
	@printf "Type=exec\n" >> ota2tcp.service
	@printf "Restart=always\n" >> ota2tcp.service
	@printf "RestartSec=5\n" >> ota2tcp.service
	@printf "\n" >> ota2tcp.service
	@printf "[Install]\n" >> ota2tcp.service
	@printf "WantedBy=multi-user.target\n" >> ota2tcp.service
	@echo "creating the symlinks"
	@sudo ln -sf $(here) $(exe_dir)
	@sudo ln -sf $(here)/$(name).service $(service_dir)
	@echo "enabling the service"
	@sudo systemctl enable $(name)
	@sudo systemctl restart $(name)

uninstall:
	@echo "stopping the over the air to tcp socket service"
	@sudo systemctl stop $(name)
	@sudo systemctl disable $(name)
	@echo "removing symlinks"
	@sudo rm -f $(service_dir)/$(name).service
