```dockerfile
# Use Python 3.12 as the base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files into the container
COPY . .

# Command to run the application (modify as needed)
CMD ["python", "your_script.py"]
``` 

Replace `"your_script.py"` with the name of your main Python file.