.PHONY:	all
all:	docstarball

docs:  Dockerfile
	docker build -t pnsodocs:latest .
	@echo
	@echo "Please run:  docker run -d -p 1313:1313 pnsodocs"
	@echo "Website will be locally served at http://localhost:1313"
	@echo

docstarball:	docs
	docker save pnsodocs:latest | gzip > pnsodocs_docker.tar.gz

clean:
	docker rmi pnsodocs:latest
