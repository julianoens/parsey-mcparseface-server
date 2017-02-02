# Parsey McParseface server

- Build the base image `tensorflow-syntaxnet` from [Dockerfile](https://github.com/tensorflow/models/blob/master/syntaxnet/Dockerfile)
```
docker build -t tensorflow-syntaxnet .
```

- Build this image `parsey-mcparseface-server` from [Dockerfile](Dockerfile)
```
docker build -t parsey-mcparseface-server .
docker run -p 80:80 parsey-mcparseface-server
```
