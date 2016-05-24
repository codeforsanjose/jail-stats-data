# JailStats Update Program

FROM frolvlad/alpine-python3

COPY image/ /
RUN apk add --update ca-certificates

ENV PORT=80
CMD ["/gateway", "-debug"]
