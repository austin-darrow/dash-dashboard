This application pulls user and system allocation/usage data from the Texas Advanced Computing Center ([TACC](https://tacc.utexas.edu)) Allocation System ([TAS](https://tacc.utexas.edu/use-tacc/allocations/)) database. Data is retrieved in monthly .xlsl files. Then, using the [Pandas](https://pandas.pydata.org/docs/) and [Plotly Dash](https://dash.plotly.com/) external Python libraries, an [Nginx](https://www.nginx.com/) web server, and a TACC-partitioned VM, it creates a visual, interactive data dashboard with filters, charts, and graphs.

The application serves two separate dashboards--a full version containing sensitive internal user data, and a lite version that only displays overall trends.

The full web app is currently hosted [here](http://129.114.38.28). Login is required.
The lite web app is currently hosted [here](http://129.114.38.28:8051).

Installation / Update
------------
1. On your local PC, pull the application files from the [GitHub repository](https://github.com/austin-darrow/dash-dashboard).
```
git clone git@github.com:austin-darrow/dash-dashboard.git
```
2. In ./assets/data/monthly reports, add all monthly reports. Reports should follow the following naming convention: utrc_report_YYYY-MM-DD_to_YYYY-MM-DD.xlsx (e.g. utrc_report_2019-12-01_to_2020-01-01.xlsx).
3. In ./assets/data, add a file named accounts.txt. This file should contain a single json dictionary with usernames as keys and passwords as values:
```
{
    "username1": "password1",
    "username2": "password2"
}
```
4. Build the image and push to DockerHub.
```
docker build -t austindarrow/dashboard:1.0 .
docker push austindarrow/dashboard:1.0
```
5. On the VM, setup the Nginx web server configuration file to reverse proxy at port 8050.
```
# /etc/nginx/sites-available/dashboard.conf
server {
        listen 80;
        listen [::]:80;

        # Change to domain name
        server_name 129.114.38.28;

        location / {
                proxy_pass http://localhost:8050;
        }
}
```
6. Pull the docker image from DockerHub.
```
docker pull austindarrow/dashboard:1.0
```
7. Start the docker image, send it to the background, and exit the VM.
```
docker run --rm -p 8050:8050 austindarrow/dashboard:1.0 && bg && exit
```