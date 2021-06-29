.PHONY: help

user := $(shell id -u -n)

service_dir := /etc/systemd/system

exe_dir := /usr/local/bin/bios/hardware
log_dir := /var/log/bios
conf_dir := /etc/bios

here := $(shell pwd)

help:
	@echo "to install hardware services\n"
	@echo "to create the conf file, run: make ota2tcp"
	@echo "make install name=ota2tcp\n"
	@echo "make uninstall name=ota2tcp\n"
	
ota2tcp:
	@echo "creating $@ conf file"
	@printf '{\n' > $@.conf
	@printf '    "interval":5\n' >> $@.conf
	@printf '}' >> $@.conf

install:
	@sudo chmod +x $(here)/$(name).py
	@if [ -f $(name).conf]; then\
	    echo "creating conf dir and populating with a conf file";\
		sudo mkdir -p $(conf_dir);\
		sudo cp $(name).conf $(conf_dir)/$(name).conf;\
		sudo chmod 666 $(conf_dir)/$(name).conf;\
	fi
	@echo "creating the log folder/file"
	@sudo mkdir -p -m 775 $(log_dir)
	@sudo chgrp -R $(user) $(log_dir)
	@echo "creating the service file"
	@printf "[Unit]\n" > $(name).service
	@printf "Description=$(name)\n" >> $(name).service
	@printf "Requires=var-log.mount systemd-timesyncd.service\n" >> $(name).service
	@printf "After=network.target redis.service mosquitto.service\n" >> $(name).service
	@printf "\n" >> $(name).service
	@printf "[Service]\n" >> $(name).service
	@printf "User=$(user)\n" >> $(name).service
	@printf "ExecStart=$(exe_dir)/$(name).py --log=$(log_dir)/$(name).log" >> $(name).service;\
	@if [ -f $(conf_dir)/$(name).conf]; then\
		printf " --conf=$(conf_dir)/$(name).conf" >> $(name).service;\
	fi
	@printf "\n"
	@printf "Type=exec\n" >> $(name).service
	@printf "Restart=always\n" >> $(name).service
	@printf "RestartSec=5\n" >> $(name).service
	@printf "\n" >> $(name).service
	@printf "[Install]\n" >> $(name).service
	@printf "WantedBy=multi-user.target\n" >> $(name).service
	@echo "creating the symlinks"
	@sudo ln -sf $(here) $(exe_dir)
	@sudo ln -sf $(here)/$(name).service $(service_dir)
	@echo "enabling the service"
	@sudo systemctl enable $(name)
	@sudo systemctl restart $(name)

uninstall:
	@echo "stopping the $(name) service"
	@sudo systemctl stop $(name)
	@sudo systemctl disable $(name)
	@echo "removing symlinks"
	@sudo rm -f $(service_dir)/$(name).service
