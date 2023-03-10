all: build run

build:
	docker build -t austindarrow/dashboard:1.0 .

run:
	docker run --rm -p 8050:8050 austindarrow/dashboard:1.0