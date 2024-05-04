from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'processing_folder'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'csv'}  # Define the set of allowed file extensions

app.secret_key = 'murraystate'

# Method to connect to MySQL
def connect_to_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="timesheet",
        password="timesheetuser123!!@@",
        database="timesheet"
    )

# Home Page route
@app.route('/')
def index():
    return render_template('index.html')
    
# Users Page route
@app.route('/users')
def users():
    conn = connect_to_mysql()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('users.html', users=users)

# Method to add user
@app.route('/add', methods=['POST'])
def add_user():
    conn = connect_to_mysql()
    cursor = conn.cursor()
    username = request.form['username']
    employeeid = request.form['employeeid']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    status = "ACTIVE"
    email = request.form['email']

    cursor.execute("INSERT INTO users (username, firstname, lastname, status, email,employeeid) VALUES (%s, %s, %s, %s, %s, %s)", (username,firstname,lastname,status,email,employeeid))
    
    conn.commit()
    conn.close()
    return redirect(url_for('index'))
    
# Time Sheet Import Page route
@app.route('/timesheetimportpage')
def timesheetimportpage():
    conn = connect_to_mysql()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('timesheetimportpage.html', users=users)

# Method to Add / Import timesheet data
@app.route('/addtimesheet', methods=['POST'])
def add_timesheet():
    file = request.files['timesheetimportfile']
    filename = file.filename
    #print ('filename')
    #print (filename) 
    # check the file name extension to be csv otherwise show error  
    if ('.' in filename and  filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
      pass    
    else:
      return jsonify({'error': 'Invalid file extension. Only CSV files are allowed.'})
      
    file_path= os.path.join(app.config['UPLOAD_FOLDER'],filename)
    
    #print (file_path)
    file.save(file_path)
    #pass the file to validate_process_timesheetdata to validate and process data
    validate_process_timesheetdata(file_path)
    
    return redirect(url_for('timesheetimportpage'))
    

def validate_process_timesheetdata(file_path):
    df= pd.read_csv(file_path)
    print (df)  
    
    for rownum, rowdata in df.iterrows():        
        errormessage = validate_row(rownum, rowdata)
        if (errormessage == '' ):
            print ("Processing Data Row: ", rownum + 1)
            errormessage = process_row(rownum, rowdata)


def validate_row(rownum, rowdata):

    # read data from rowdata 
    username = rowdata['username']
    employeeid = rowdata['employeeid']
    startdatetime = rowdata['startdatetime']
    enddatetime = rowdata['enddatetime']
    breakinminutes = rowdata['breakinminutes']
    
    rownum = rownum +1 
    
    errormessage =''
    hours=0.0
    start_time=''
    end_time =''
    
    #print (username)
    #print (employeeid)
    #print (startdatetime)
    #print (enddatetime)
    #print (breakinminutes)
    
    #check username and employeeid are present
    #
    try:        
            
        # Convert the strings to datetime objects
        
        if pd.isna(username):
           errormessage = "\nUsername is required. Error on row: " + str(rownum)
           
        if pd.isna(employeeid):          
           errormessage = errormessage + "\nEmployeeID is required. Error on row: " + str(rownum) 
        
        try:
           start_time = datetime.strptime(startdatetime, "%m/%d/%Y %I:%M%p")
           end_time = datetime.strptime(enddatetime, "%m/%d/%Y %I:%M%p")
           
           current_datetime = datetime.now()
           
           #print (start_time)
           #print (end_time)
           #print (current_datetime)
           
           # Find the difference in days, seconds, and microseconds.
           time_difference = end_time - start_time
        
           # Change to hours
           hours = time_difference.total_seconds() / 3600
           
           print("Time difference:", hours)          
           
           if (start_time > current_datetime or  end_time > current_datetime):
                errormessage = errormessage + "\nStart and End Date time cannot be in the Future. Error on row: " +str(rownum)             
           
        except ValueError as e:  
           errormessage = errormessage + "\nError Parsing Date. Error on row: " + str(rownum)+" Date format Error. Valid format exmaple: 03/13/2024 08:00AM" 
        
        
        if (hours < 0.0 and (start_time == end_time) ):
              errormessage = errormessage + "\nEnd Date time cannot be before or same as Start Date time. Error on row: " +str(rownum) 
              
        if hours > 0.0:
           try:
               breakinminutes = int(breakinminutes)
               
               if breakinminutes > 0:
                  if ((hours - breakinminutes/60.00) < 0):
                      errormessage = errormessage + "\nData Validation Error on Row: " + str(rownum)+" Break hour is bigger than hours worked."   
               
           except ValueError as e:  
               errormessage = errormessage + "\nError Parsing Break (breakinminutes) Data. Error on row: " + str(rownum)+" breakinminutes value should be a number in minutes."        
           
        if errormessage != '':
           raise ValueError(errormessage)
        return errormessage
        
    except ValueError as e:    
       flash(str(e), 'error')
       return redirect(url_for('add_timesheet'))  
       
    
def process_row(rownum, rowdata):
    # read data from rowdata 
    username = rowdata['username']
    employeeid = rowdata['employeeid']
    startdatetime = rowdata['startdatetime']
    enddatetime = rowdata['enddatetime']
    breakinminutes = rowdata['breakinminutes']
    
    errormessage = ''
    
    start_time = datetime.strptime(startdatetime, "%m/%d/%Y %I:%M%p")
    end_time = datetime.strptime(enddatetime, "%m/%d/%Y %I:%M%p")
    
    time_difference = end_time - start_time
        
    # Change to hours
    hours = time_difference.total_seconds() / 3600    
    # Substract break
    hours = hours - (breakinminutes/60)
    
    rownum = rownum +1 
    
    
    try: 
        
        conn = connect_to_mysql()
        cursor = conn.cursor()         
        cursor.execute("INSERT INTO timesheet (username, employeeid, startdatetime, enddatetime, hours,breakinminutes) VALUES (%s, %s, %s, %s, %s, %s)", (username,employeeid,start_time,end_time,hours,breakinminutes))    
        conn.commit()
        flash(('Processed Row: ' + str(rownum)), 'success')
        
    except mysql.connector.Error as error:
        if error.errno == mysql.connector.errorcode.ER_DUP_ENTRY:
           print("Duplicate entry detected. Please handle accordingly.")
           print("Row num:", rownum)
        else:
           print("An error occurred:", error)
        flash(str(error)+ ('Error on row: ' + str(rownum)), 'error')
     
    finally:
       # Close the database connection
       if 'conn' in locals() and conn.is_connected():
           cursor.close()
           conn.close()
   
    return redirect(url_for('add_timesheet'))


# Method to Time Sheet Report Page
@app.route('/timesheetreport')
def timesheetreport():
    conn = connect_to_mysql()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM timesheet where startdatetime >= (current_date()  - INTERVAL 30 DAY) or enddatetime >= (current_date()  - INTERVAL 30 DAY)")
    timesheetdata = cursor.fetchall()
    cursor.execute("SELECT * FROM users")
    userdata = cursor.fetchall()
    conn.close()
    return render_template('timesheetreportpage.html', timesheetdata=timesheetdata, userdata=userdata, defaultuserfilter=None)
    

# Method to search timesheet data
@app.route('/searchtimesheet', methods=['POST'])
def searchtimesheet():
    sql =""
    conn = connect_to_mysql()
    cursor = conn.cursor()
    whereClause = None   
  
    #print ("whereClause")      
    #print (whereClause)
    
    if 'datetimelocal' in request.form and request.form.get('datetimelocal'):
       datetimelocal = request.form['datetimelocal']
       #print (datetimelocal)
       input_datetime = datetime.strptime(datetimelocal, "%Y-%m-%dT%H:%M")
       mysql_datetime = input_datetime.strftime("%Y-%m-%d %H:%M:%S")
       #print (mysql_datetime)
       
       whereClause =  "startdatetime >='" + mysql_datetime + "' or enddatetime >='" + mysql_datetime + "'"
    if 'select_list' in request.form and request.form.get('select_list'):
    
       #print ("request.form['select_list']")      
       #print (request.form['select_list'])
       
       select_list_values = list(request.form['select_list'].replace("'", "").replace("(", "").replace(")", "").replace(" ", "").split(","))     
       
       
       username = select_list_values[1]
       employeeid = select_list_values[2]
       if whereClause is not None:
          whereClause = whereClause + " and username='"+username + "' and employeeid='"+ employeeid + "'"
       else:
          whereClause = "username='"+username + "' and employeeid='"+ employeeid + "'"
     
    if whereClause is not None:
       sql =  "SELECT * FROM timesheet where "+ whereClause
    else:
       sql =  "SELECT * FROM timesheet"
       
    #print("whereClause")    
    #print(whereClause)
    
    #print("sql")    
    #print(sql)
    
    cursor.execute(sql)
    timesheetdata = cursor.fetchall()    
    #print (timesheetdata)
    cursor.execute("SELECT * FROM users")
    userdata = cursor.fetchall()
    conn.close()
    
    return render_template('timesheetreportpage.html', timesheetdata=timesheetdata, userdata=userdata, defaultuserfilter=None)
    
if __name__ == '__main__':
    app.run(debug=True)
