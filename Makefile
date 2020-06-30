.PHONY:	all
all:	latest 

.PHONY:	latest
latest:	Dockerfile
	docker build -t pnsodocs:latest .
	@echo docker save pnsodocs:latest | gzip > pnsodocs_docker.tar.gz
	@echo
	@echo "Please run:  docker run --rm -d -p 1313:1313 pnsodocs"
	@echo "Website will be locally served at http://localhost:1313"
	@echo

clean:
	docker rmi pnsodocs:latest
