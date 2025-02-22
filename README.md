# **NLP-Excel-Engine**

NLP-Excel-Engine is a tool that combines **LLM (Large Language Models) and Excel** to automate  **data analysis, transformation, and insights generation** . It enables users to process both  **structured and unstructured data** , perform  **mathematical and aggregation operations** , and more.

## **How to Run This Application**

### **1. Environment Setup**

* This project uses **pyenv** for Python environment management. You can install **pyenv** by following the instructions [here](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation "pyenv installation").
* Alternatively, you can use any other available environment management tools.
* Once the environment is ready, install dependencies using:
  ```
  pip install -r requirements.txt
  ```

### **2. Running the Application**

* For development, simply run:
  ```
  docker-compose up --build
  ```
* Once the application is up and running, you can check its health status using the  /**health endpoint** .
* Access the app at: http:.//localhost:5001
* Added docker-componse to reload docker build when the files are updated.
