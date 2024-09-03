# Start from a minimal base image with Conda installed
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app

# Copy the environment file and install dependencies
COPY environment.yml .

# Create the environment and activate it
RUN conda env create -f environment.yml

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "fastapi-env", "/bin/bash", "-c"]

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
