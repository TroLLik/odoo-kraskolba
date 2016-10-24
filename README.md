## Для запуска экосистемы разработчика 
* Идем в ./Docker/odoo-dev-ecosys
* Правим пути в docker-compose.yml
* Если хотим логи в консоль, коментим (;) строку logfile = /mnt/log/odoo-server.log в ./Docker/odoo-dev-ecosys/odoo-app/odoo.conf
* Если хотим логи в файл, нужно в хост системе выполнить

	$ adduser --system --shell=/bin/false -no-create-home -u 1488 --group odoo
	$ chown -R odoo:odoo /путь/до/папки/с/логами

* Выполняем

	docker-compose up