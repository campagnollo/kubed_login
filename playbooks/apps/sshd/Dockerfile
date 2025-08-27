# apps/sshd/Dockerfile
FROM alpine:3.20

# Install OpenSSH
RUN apk add --no-cache openssh \
 && ssh-keygen -A \
 && adduser -D -s /bin/sh dev \
 && echo "dev:dev" | chpasswd

# Expose SSH port
EXPOSE 22

# Run sshd in the foreground
CMD ["/usr/sbin/sshd","-D","-e"]
