.PHONY:	all
all:	latest 

.PHONY:	latest
latest:	Dockerfile
	docker build -t pnsodocs:latest .
	@echo
	@echo "Please run:  docker run -d -p 1313:1313 pnsodocs"
	@echo "Website will be locally served at http://localhost:1313"
	@echo


