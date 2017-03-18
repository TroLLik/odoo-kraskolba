## Для запуска экосистемы разработчика 
* Идем в ./Docker/odoo-dev-ecosys
* Если хотим логи в консоль, коментим (;) строку logfile = /mnt/log/odoo-server.log в ./Docker/odoo-dev-ecosys/odoo-app/odoo.conf
* Если хотим логи в файл, нужно в хост системе выполнить

	$ adduser --system --shell=/bin/false -no-create-home -u 1488 --group odoo
	$ chown -R odoo:odoo /путь/до/папки/с/логами

* Ставим compose вот [так](https://docs.docker.com/compose/install/)
* Выполняем

	docker-compose up

* Получаем:
	* odoo на http://localhost:8069 (логин/пароль:admin/admin)
	* pgadm4 на http://localhost:5050 (настраиваем на сервер с именем:pg логин/пароль:odoo/odoo бд:odoo)
