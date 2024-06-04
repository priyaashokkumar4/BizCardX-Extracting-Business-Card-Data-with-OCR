import streamlit as st
from streamlit_option_menu import option_menu
from PIL  import Image
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import pprint
import io
import mysql.connector


mydb = mysql.connector.connect(
          host="localhost",
          user="root",
            password="",
            database = "BIZCARDX"  
          )
print(mydb)
             

mycursor = mydb.cursor(buffered=True)



def image_to_text(path):

  input_img = Image.open(path)
  #convert image to array:
  image_arr = np.array(input_img)
  reader  =  easyocr.Reader(['en'])
  text = reader.readtext(image_arr,detail=0)
  return  text , input_img

#text_img ,input_img =  image_to_text("4.png")



def extracted_text(texts):
  extracted_dict = {"NAME":[], "DESIGNATION":[],"COMPANY_NAME":[] , "CONTACT":[],"EMAIL":[],"WEBSITE":[],
                    "ADDRESS":[],"PINCODE":[]}
  extracted_dict["NAME"].append(texts[0])
  extracted_dict["DESIGNATION"].append(texts[1])

  for i in range(2,len(texts)):

      if texts[i].startswith("+") or (texts[i].replace("-","").isdigit()and '-' in texts[i]):
        extracted_dict["CONTACT"].append(texts[i])

      elif "@" in texts[i] and ".com" in texts[i]:
        extracted_dict["EMAIL"].append(texts[i])

      elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw"in texts[i] or "wwW"in texts[i]:
        small= texts[i].lower()
        extracted_dict["WEBSITE"].append(small)

      elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
        extracted_dict["PINCODE"].append(texts[i])

      elif re.match(r'^[A-Za-z]',texts[i]):
        extracted_dict["COMPANY_NAME"].append(texts[i])

      else:
        remove_colons = re.sub(r'[,;]','',texts[i])
        extracted_dict["ADDRESS"].append(remove_colons)

  for key,value in extracted_dict .items():
    if len(value)>0:
      concadenate = " ".join(value)
      extracted_dict[key] = [concadenate]
    else:
      value = "NA"
      extracted_dict[key] = [value]




  return(extracted_dict)


#extracted_text(text_img)





st.set_page_config(layout = "wide")
st.title("EXTRACT BUSINESS CARD WITH 'OCR' ")
with st.sidebar:
    select = option_menu("Main Menu",["Home","Upload & Modify","Delete"],
                         icons=['house','cloud-upload', 'delete']  )
    
if  select == "Home" :
    
   st.write("STEP 1:  BizCardX: Extracting Business Card Data with OCR ")
   st.write("STEP 2:  Extract the text from the  business card by using OCR")
   st.write('''STEP 3:  OCR (optical character recognition) is the use of technology to distinguish printed or
                             handwritten text characters inside digital images of physical documents''')
   st.write("STEP 4 : Extracted the data from the card then  convert into dictionary")
   st.write("STEP 5 : Dictionary into DataFrame that should display in STREAMLIT")
   st.write("STEP 6 : If Modify any  data  that  modifed data should  updated in sql bench")
   st.write('''STEP 7 : If you delete the data  by choosing the particular NAME  AND  DESIGNATION 
                      that data should deleted from SQL BENCH''')
   img  = Image.open("bcard.png")
   st.image(img, width  =400)
   img1  = Image.open("priya.png")
   st.image(img1, width  =400)
   
   

elif select == "Upload & Modify":
    image = st.file_uploader("UPLOAD THE IMAGE",type= ["png","jpg","jpeg"])

    if image is not None:
       st.image(image , width=400)

       text_img ,input_img =  image_to_text(image)

       word_dict = extracted_text(text_img)

       if word_dict:
          st.text("TEXT  IS  EXTRACTED FROM CARD")

       df=pd .DataFrame(word_dict)

       #coverting image to bytes:
       Image_bytes =io.BytesIO()
       Image_bytes =io.BytesIO()
       input_img.save(Image_bytes , format = "PNG")

       image_data = Image_bytes.getvalue()

       #creating Dict:

       data ={"IMAGE":[image_data]}

       df_1 = pd.DataFrame(data)

       concat_df = pd.concat([df,df_1],axis=1)
       st.dataframe(concat_df)

       button_1 = st.button("Save")
       if  button_1:


          mycursor.execute('''CREATE TABLE IF NOT EXISTS  BIZCARDX (NAME VARCHAR(250),
                                         DESIGNATION VARCHAR (250),
                                         COMPANY_NAME VARCHAR(250),
                                         CONTACT VARCHAR(250),
                                         EMAIL VARCHAR(250) PRIMARY KEY,
                                         WEBSITE TEXT,
                                         ADDRESS TEXT,
                                         PINCODE VARCHAR(255),
                                         IMAGE TEXT)''')

          mydb.commit()
          insert_query = ('''INSERT INTO BIZCARDX (NAME ,DESIGNATION ,COMPANY_NAME ,CONTACT ,EMAIL,WEBSITE ,ADDRESS,PINCODE,IMAGE)
                                          values (%s ,%s,%s,%s,%s,%s,%s,%s,%s)''')

          datas = concat_df.values.tolist()[0]
          mycursor.execute(insert_query,datas)
          mydb.commit()      
    

    #method = st.option_menu("SELECT THE Method",["None","Preview","Modify"],orientation = "horizontal")
    method = option_menu(
            "SELECT THE METHOD",
            ["None", "Preview", "Modify"],
            icons=["dash", "eye", "pencil"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal"
        )

    if method == "None":
      st.write("")

    elif method == "Preview":
       select_qyery =  "select * from BIZCARDX "
       mycursor.execute(select_qyery)
       table = mycursor.fetchall()
       mydb.commit()
       table_df = pd.DataFrame(table,columns=("NAME" ,"DESIGNATION" ,"COMPANY_NAME" ,"CONTACT" ,"EMAIL","WEBSITE" ,
                                                "ADDRESS","PINCODE","IMAGE"))
       st.dataframe(table_df) 
              

    elif method == "Modify":
       select_qyery =  "select * from BIZCARDX "
       mycursor.execute(select_qyery)
       table = mycursor.fetchall()
       mydb.commit()
       table_df = pd.DataFrame(table,columns=("NAME" ,"DESIGNATION" ,"COMPANY_NAME" ,"CONTACT" ,"EMAIL","WEBSITE" ,
                                                "ADDRESS","PINCODE","IMAGE"))
       st.dataframe(table_df)

       selected_name = st.selectbox("SELECT THE NAME",table_df["NAME"])

       df_3 = table_df[table_df["NAME"] == selected_name]
       

       df_4 = df_3.copy()
       

       modify_name = st.text_input("NAME",df_3["NAME"].unique()[0])
       modify_disignation = st.text_input("disignation",df_3["DESIGNATION"].unique()[0])
       modify_comapnyname = st.text_input("comapnyname",df_3["COMPANY_NAME"].unique()[0])
       modify_contact = st.text_input("contact",df_3["CONTACT"].unique()[0])
       modify_email = st.text_input("email",df_3["EMAIL"].unique()[0])
       modify_website = st.text_input("website",df_3["WEBSITE"].unique()[0])
       modify_address = st.text_input("address",df_3["ADDRESS"].unique()[0])
       modify_pincode = st.text_input("pincode",df_3["PINCODE"].unique()[0])
       modify_image = st.text_input("image",df_3["IMAGE"].unique()[0])

       df_4["NAME"] = modify_name
       df_4["DESIGNATION"] = modify_disignation
       df_4["COMPANY_NAME"] = modify_comapnyname
       df_4["CONTACT"] = modify_contact
       df_4["EMAIL"] = modify_email
       df_4["WEBSITE"] = modify_website
       df_4["ADDRESS"] = modify_address
       df_4["PINCODE"] = modify_pincode
       df_4["IMAGE"] = modify_image

       st.dataframe(df_4)

       button_3 = st.button("Modify",use_container_width=400)

       mycursor.execute(f"DELETE FROM BIZCARDX WHERE NAME = '{selected_name}'")
       mydb.commit()

       insert_query = ('''INSERT INTO BIZCARDX (NAME ,DESIGNATION ,COMPANY_NAME ,CONTACT ,EMAIL,WEBSITE ,ADDRESS,PINCODE,IMAGE)
                                          values (%s ,%s,%s,%s,%s,%s,%s,%s,%s)''')

       datas = df_4.values.tolist()[0]
       mycursor.execute(insert_query,datas)
       mydb.commit() 


elif select =="Delete":
    select_qyery =  "select  NAME from BIZCARDX "
    mycursor.execute(select_qyery)
    table1 = mycursor.fetchall()
    mydb.commit()

    names  = []

    for i in table1:
         names.append(i[0])
    name_select = st.selectbox("SELECT THE NAME",names) 

    select_qyery2 =  f"select  DESIGNATION from BIZCARDX  where NAME = '{name_select}'"
    mycursor.execute(select_qyery2)
    table2 = mycursor.fetchall()
    mydb.commit()

    designation  = []

    for j in table2:
        designation.append(j[0])

    des_select = st.selectbox("SELECT THE DESIGNATION",designation) 

    if name_select and des_select:
       
       st.write (f"Select Name:'{name_select}'")
       st.write("")
       
       st.write(f"Select Designation:'{des_select}'")
       st.write("")
      
       st.write("")
       remove = st.button("DELETE",use_container_width= True)

       if remove:
          mycursor.execute(f" DELETE FROM BIZCARDX  WHERE Name ='{name_select}' AND DESIGNATION = '{des_select}' ")
          mydb.commit()
          st.write("deleted the text")
