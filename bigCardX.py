import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import mysql.connector
import os
import cv2
import matplotlib.pyplot as plt
import re
import numpy as np

#connecting with mysql database
mydb = mysql.connector.connect(
   host="localhost",
   user="root",
   password="" ,
   database="bigcardx" )

mycursor = mydb.cursor(buffered=True)

 #creating mysql table
mycursor.execute('''CREATE TABLE IF NOT EXISTS card_info
                   (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    company_name TEXT,
                    card_holder TEXT,
                    designation TEXT,
                    mobile_number VARCHAR(50),
                    email TEXT,
                    website TEXT,
                    area TEXT,
                    city TEXT,
                    state TEXT,
                    pin_code VARCHAR(10)
                    )''')

#setting up page configuration
st.set_page_config(
    page_title="BigCardX: Extracting Business Card Data with OCR|By Divyalakhsmi",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("<h1 style='text-align: center; color: black;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

#https://wallpaper.csplague.com/wp-content/uploads/2021/12/100-Free-Vector-Hand-drawn-minimal-background.jpg
#https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRKrvsm3c5095u4OuaDFyT6cXSEHqXcyos5IA&usqp=CAU

#setting backgroung image
def setting_bg():
    st.markdown(f""" <style>.stApp {{
                        background: url("https://wallpaper.csplague.com/wp-content/uploads/2021/12/100-Free-Vector-Hand-drawn-minimal-background.jpg");
                        background-size: cover}}
                     </style>""",unsafe_allow_html=True) 
setting_bg()

#creating option menu
with st.sidebar:
    select = option_menu(None, ["Home","Upload & Extract","Modify"],
                     icons=["house","cloud-upload","pencil-square"],
                     default_index=0,
                     orientation = "vertical",
                     styles={"nav-link": {"font-size": "35px", "text-align": "centre", "margin": "0px", "--hover-color": "#6495ED"},
                               "icon": {"font-size": "35px"},
                               "container" : {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#6495ED"}})
    
#Initializing the easyocr reader
#en - English
reader = easyocr.Reader(['en'])

if select == 'Home':
    st.markdown("## :violet[**TECHNOLOGIES USED :**] :red[*Python,easy OCR, Streamlit, SQL, Pandas*]")
    st.markdown("## :violet[**Overview :**] :red[*In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information*]")
 
if not os.path.exists("uploaded_card"):
    os.makedirs("uploaded_card")

if select == "Upload & Extract":
    st.markdown("### :violet[Upload a Business Card]")
    uploaded_card = st.file_uploader("upload here",label_visibility="collapsed",type=["png","jpeg","jpg"])
           
    if uploaded_card is not None:
         # Read the image using OpenCV
        image = cv2.imdecode(np.fromstring(uploaded_card.read(), np.uint8), 1)
        # Display the uploaded image
        st.image(image, caption='Uploaded business card image', use_column_width=True)
        # Create a button to extract information from the image
        #if st.button('Extract Information'):
        # Call the function to extract the information from the image
        bounds = reader.readtext(image, detail=0,paragraph=False)
        # Convert the extracted information to a string
        text = "\n".join(bounds)
        #st.write(f'<h1 style="color:#E079E5"> {text}</h1>', unsafe_allow_html=True)
        
        #creating list to store all the data
        data = {"company_name" : [],
                "card_holder" : [],
                "designation" : [],
                "mobile_number" :[],
                "email" : [],
                "website" : [],
                "area" : [],
                "city" : [],
                "state" : [],
                "pin_code" : []
               }
        
        def get_data(res):
            for ind,i in enumerate(res):

                # To get WEBSITE_URL
                if "www " in i.lower() or "www." in i.lower():
                    data["website"].append(i)
                elif "WWW" in i:
                    data["website"] = res[4] +"." + res[5]

                # To get EMAIL ID
                elif "@" in i:
                    data["email"].append(i)

                # To get MOBILE NUMBER
                elif "-" in i:
                    data["mobile_number"].append(i)
                    if len(data["mobile_number"]) ==2:
                        data["mobile_number"] = " & ".join(data["mobile_number"])

                # To get COMPANY NAME  
                elif ind == len(res)-1:
                    data["company_name"].append(i)

                # To get CARD HOLDER NAME
                elif ind == 0:
                    data["card_holder"].append(i)

                # To get DESIGNATION
                elif ind == 1:
                    data["designation"].append(i)

                # To get AREA
                if re.findall('^[0-9].+, [a-zA-Z]+',i):
                    data["area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+',i):
                    data["area"].append(i)

                # To get CITY NAME
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*',i)
                if match1:
                    data["city"].append(match1[0])
                elif match2:
                    data["city"].append(match2[0])
                elif match3:
                    data["city"].append(match3[0])

                # To get STATE
                state_match = re.findall('[a-zA-Z]{9} +[0-9]',i)
                if state_match:
                     data["state"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);',i):
                    data["state"].append(i.split()[-1])
                if len(data["state"])== 2:
                    data["state"].pop(0)

                # To get PINCODE        
                if len(i)>=6 and i.isdigit():
                    data["pin_code"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]',i):
                    data["pin_code"].append(i[10:])

        get_data(bounds)
        
        #FUNCTION TO CREATE DATAFRAME
        def create_df(data):
            df = pd.DataFrame(data)
            return df
        
        df = create_df(data)

        st.success("### Data Extracted!")
        st.write(df)
        
        if st.button("Upload to Database"):
            for i,row in df.iterrows():
                #here %S means string values 
                query = """INSERT INTO card_info(company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                mycursor.execute(query, tuple(row))
                # the connection is not auto committed by default, so we must commit to save our changes
                mydb.commit()
            st.success("#### Uploaded to database successfully!")
            st.balloons()

if select == "Modify":
    
    st.markdown("## :violet[Alter or Delete the data here]")
    tab1,tab2 =st.tabs([":black[Alter]",":black[Delete]"])
    try:
        #creating tab to update the data
        with tab1:
            mycursor.execute("SELECT card_holder FROM card_info")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox(":violet[Select a card holder name to update]", list(business_cards.keys()))
            st.markdown("#### :violet[Update or modify any data below]")
            mycursor.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_info WHERE card_holder=%s",
                            (selected_card,))
            result = mycursor.fetchone()

            # DISPLAYING ALL THE INFORMATIONS
            company_name = st.text_input(":violet[Company_Name]", result[0])
            card_holder = st.text_input(":violet[Card_Holder]", result[1])
            designation = st.text_input(":violet[Designation]", result[2])
            mobile_number = st.text_input(":violet[Mobile_Number]", result[3])
            email = st.text_input(":violet[Email]", result[4])
            website = st.text_input(":violet[Website]", result[5])
            area = st.text_input(":violet[Area]", result[6])
            city = st.text_input(":violet[City]", result[7])
            state = st.text_input(":violet[State]", result[8])
            pin_code = st.text_input(":violet[Pin_Code]", result[9])

            if st.button("Commit changes to DB"):
                # Update the information for the selected business card in the database
                mycursor.execute("""UPDATE card_info SET company_name=%s,card_holder=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pin_code=%s
                                    WHERE card_holder=%s""", (company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,selected_card))
                mydb.commit()
                st.success("Information updated in database successfully.")
                st.balloons()
        
        # creating tab2 to delete data from the database
        with tab2:
            mycursor.execute("SELECT card_holder FROM card_info")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox(":violet[Select a card holder name to Delete]", list(business_cards.keys()))
            st.write(f"### :violet[You have selected :red[**{selected_card}'s**] card to delete]")
            st.write("#### :violet[Proceed to delete this card?]")

            if st.button("Yes Delete Business Card"):
                mycursor.execute(f"DELETE FROM card_info WHERE card_holder='{selected_card}'")
                mydb.commit()
                st.success("Business card information deleted from database.")
    except:
        st.warning("There is no data available in the database")
    
    if st.button("View updated data"):
        mycursor.execute("select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from card_info")
        updated_df = pd.DataFrame(mycursor.fetchall(),columns=["Company_Name","Card_Holder","Designation","Mobile_Number","Email","Website","Area","City","State","Pin_Code"])
        st.write(updated_df)
                    
