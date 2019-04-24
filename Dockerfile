FROM debian:jessie-slim AS release

LABEL maintainer="Videocoin" description="admin panel for db managment"

RUN apt update && apt upgrade -y
RUN apt install mysql-client ca-certificates -y

WORKDIR /go/src/github.com/VideoCoin/adminpanel


ADD bin/admin ./

EXPOSE 9077

ENTRYPOINT [ "./admin" ]
