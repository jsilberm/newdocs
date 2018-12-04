# Static website for Pensando Docs

The [Hugo](https://gohugo.io/documentation/) static website generator is a pre-requisite.

Once Hugo is installed:
```
git clone git@github.com:pensando/docs.git
cd docs
hugo server
```

Website will be locally served at [http://localhost:1313/](http://localhost:1313/)

# Or Run as a Container

```
 docker build -t pnsodocs .
 docker run -d -p 1313:1313 pnsodocs
```

Website will be locally served at [http://localhost:1313/](http://localhost:1313/)


