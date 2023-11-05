# BizCardX-Extracting-Business-Card-Data-with-OCR
## INTRODUCTION
Developing a Streamlit application that allows users to
upload an image of a business card and extract relevant information from it using
easyOCR. The extracted information include the company name, card holder
name, designation, mobile number, email address, website URL, area, city, state,
and pin code. The extracted information is displayed in the application's
graphical user interface (GUI). It allow users to save the extracted information into
a database and the database able to store multiple entries, each with its own extracted
information.

## INSTALLATION
To run this project, you need to install the following packages:
`````
pip install easyocr
pip install pandas
pip install mysql-connector-python
pip install streamlit

`````` 
## APPROACH
1. **Install the required packages:** Install Python, Streamlit, easyOCR, and a database management system like SQLite or MySQL.
2. **Design the user interface:** Create a simple and intuitive user interface using
Streamlit that guides users through the process of uploading the business
card image and extracting its information.
3. **Implement the image processing and OCR:** Use easyOCR to extract the
relevant information from the uploaded business card image. 
4. **Display the extracted information:** Once the information has been extracted,
display it in a clean and organized manner in the Streamlit GUI. 
5. **Implement database integration:** Use a database management system
MySQL to store the extracted information. You can use SQL queries to create tables, insert data,
and retrieve data from the database, Update the data and Allow the user to
delete the data through the streamlit UI.
