# Sample run
# docker run -d -v /share/homes/sdrzymala/narnia/data:/app/data pythonpudelekparser --log_path="/app/data/pudelekparserlog.txt" --selenium_driver_path="/app/chromedriver" --db_connectionstring="DRIVER={ODBC Driver 17 for SQL Server};SERVER=XX.XX.XX.XX;DATABASE=Pudelek;UID=sa;PWD=XXX" --run_type="al" --al_start_page="1" --al_no_pages="5" --ad_no_pages="10"
# docker run -d -v /share/homes/sdrzymala/narnia/data:/app/data pythonpudelekparserad --log_path="/app/data/pudelekparserlog_ad.txt" --selenium_driver_path="/app/chromedriver" --db_connectionstring="DRIVER={ODBC Driver 17 for SQL Server};SERVER=XX.XX.XX.XX;DATABASE=Pudelek;UID=sa;PWD=XXX" --run_type="ad" --al_start_page="1" --al_no_pages="5" --ad_no_pages="10"	

# Use an official Python runtime as a parent image
FROM python:latest

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Define build environment
ARG DEBIAN_FRONTEND=noninteractive

# handle SQL connection and selenium
RUN apt-get update && \
    pip install --upgrade pip && \
    apt-get install --no-install-recommends -fy curl && apt-get clean && \
    apt-get install --no-install-recommends -fy apt-transport-https && apt-get clean && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install --no-install-recommends -fy msodbcsql17 && \
    ACCEPT_EULA=Y apt-get install --no-install-recommends -fy mssql-tools && \
    apt-get install -fy --no-install-recommends unixodbc-dev && apt-get clean && \
    apt-get install -fy --no-install-recommends gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1  libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator3-1 libnss3 lsb-release xdg-utils && apt-get clean && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install && \
    apt-get install --no-install-recommends -fy unzip && apt-get clean && \
    wget https://chromedriver.storage.googleapis.com/2.46/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World
ENV IS_RUNNING_FROM_DOCKER Yes

# Define entry point
ENTRYPOINT ["python", "pudelekparser.py"]