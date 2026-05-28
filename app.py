from flask import Flask, render_template, request, redirect
from database import get_connection
app = Flask(__name__)
@app.route('/')
def home():
    return render_template("index.html")
@app.route('/inventory')
def inventory():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory(
            med_id INT PRIMARY KEY,
            med_name VARCHAR(50),
            mfr char(12) not null,
            exp varchar(10),
            stock INT,
            mrp FLOAT
        )
    """)
    cur.execute("SELECT * FROM inventory")
    medicines = cur.fetchall()
    con.close()
    return render_template("inventory.html", medicines=medicines)

@app.route('/add', methods=['GET', 'POST'])
def add_medicine():
    if request.method == 'POST':
        med_id = request.form['med_id']
        med_name = request.form['med_name']
        mfr=request.form['mfr']
        exp=request.form['exp']
        stock = request.form['stock']
        mrp = request.form['mrp']
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO inventory VALUES (%s,%s,%s,%s,%s,%s)",
            (med_id, med_name, mfr, exp, stock, mrp)
        )
        con.commit()
        con.close()
        return redirect('/inventory')
    return render_template("add_medicine.html")

@app.route('/display_medicine',methods=['GET','POST'])
def display_medicine():
    if request.method=='POST':
        med_id=request.form['med_id']
        con=get_connection()
        cur=con.cursor()
        cur.execute(
            "Select * from inventory where med_id=%s",
            (med_id,)
        )
        medicine=cur.fetchone()
        con.close()
        return render_template("search_medicine_result.html",medicine=medicine)
    return render_template("search_medicine.html")

@app.route('/update',methods=['GET','POST'])
def update_medicine():
    if request.method == 'POST':
        MedID=request.form['MedID']
        newstock=request.form['newstock']
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "update inventory set stock=%s where med_id=%s",
            (newstock,MedID)
        )
        con.commit()
        con.close()
        return redirect('/inventory')
    return render_template("update_medicine.html")

@app.route('/delete', methods=['GET', 'POST'])
def delete_medicine():
    if request.method == 'POST':
        IDmed = request.form['IDmed']
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "DELETE FROM inventory WHERE med_id = %s",
            (IDmed,)
        )
        con.commit()
        con.close()
        return redirect('/inventory')
    return render_template("delete_medicine.html")

@app.route('/Customer')
def customer():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customer(
            cust_id INT PRIMARY KEY,
            name VARCHAR(10) not null,
            age INT
        )
    """)
    cur.execute("SELECT * FROM customer")
    customers = cur.fetchall()
    con.close()
    return render_template("customer.html", customers=customers)

@app.route('/addcustomer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        cust_id = request.form['cust_id']
        name = request.form['name']
        age = request.form['age']
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO customer VALUES (%s,%s,%s)",
            (cust_id,name,age)
        )
        con.commit()
        con.close()
        return redirect('/Customer')
    return render_template("add_customer.html")

@app.route('/updatecustomer',methods=['GET','POST'])
def update_customer():
    if request.method == 'POST':
        cust_id=request.form['cust_id']
        age=request.form['age']
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "update customer set age=%s where cust_id=%s",
            (age,cust_id)
        )
        con.commit()
        con.close()
        return redirect('/Customer')
    return render_template("update_customer.html")

@app.route('/deletecustomer', methods=['GET', 'POST'])
def delete_customer():
    if request.method == 'POST':
        cust_id = request.form['cust_id']
        con = get_connection()
        cur = con.cursor()
        cur.execute(
            "DELETE FROM customer WHERE cust_id = %s",
            (cust_id,)
        )
        con.commit()
        con.close()
        return redirect('/Customer')
    return render_template("delete_customer.html")

@app.route('/Purchase_History')
def Purchase_History():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Purchase_History(
            pur_id INT PRIMARY KEY,
            cust_id int,
            med_id int,
            med_name varchar(20) not null,
            mfr varchar(15),
            p_date varchar(10),
            qty int,
            mrp decimal(10,2),
            value decimal(10,2),
            foreign key(cust_id) references customer(cust_id)
        )
    """)
    cur.execute("SELECT * FROM Purchase_History")
    pur_history = cur.fetchall()
    con.close()
    return render_template("Purchase_History.html", pur_history=pur_history)

@app.route('/add_purchase_history_record',methods=['GET','POST'])
def add_purchase_history_record():
    if request.method=='POST':
        pid=request.form['purchase_id']
        cid=request.form['customer_id']
        m_id=request.form['med_id']
        mname=request.form['med_name']
        mfr=request.form['mfr']
        p_date=request.form['p_date']
        con=get_connection()
        cur=con.cursor()
        cur.execute(
            "select stock from inventory where med_id=%s",
            (m_id,)
        )
        inv_stock=cur.fetchone()[0]
        print('-----------------------------')
        print("Stock of",mname,"in inventory is",inv_stock)
        print('-----------------------------')
        qty=int(request.form['qty'])
        if qty>inv_stock:
            print("------------------")
            print("Sorry, insufficient stock")
            return "Insufficient stock"
        cur.execute(
            "Update inventory set stock=stock-%s where med_id=%s",
            (qty,m_id)
        )
        cur.execute(
            "select stock from inventory where med_id=%s",
            (m_id,)
        )
        row=cur.fetchone()
        if not row:
            return "Medicine not found"
        inv_stock=row[0]
        print('------------------------------------------------------------')
        print("The stock of",mname,"has been reduced from",inv_stock,"to",row)
        print('------------------------------------------------------------')
        mrp=float(request.form['mrp'])
        val=qty*mrp
        cur.execute(
            "insert into Purchase_History values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (pid,cid,m_id,mname,mfr,p_date,qty,mrp,val)
        )
        con.commit()
        con.close()
        return redirect('/Purchase_History')
    return render_template("add_purchase_history_record.html")

@app.route('/display_sales_report',methods=['GET','POST'])
def sales_report():
    if request.method=='POST':
        con=get_connection()
        cur=con.cursor()
        purchase_date=request.form['pur_date']
        cur.execute(
            "select med_id,med_name,sum(qty),sum(value) from Purchase_History where p_date=%s group by med_id,med_name",
            (purchase_date,)
        )
        rec=cur.fetchall()
        cur.execute(
            "select sum(value) from Purchase_History where p_date=%s",
            (purchase_date,)
        )
        grand_total=cur.fetchone()[0]
        print("\t\t SALES REPORT")
        print("Date: ",purchase_date)
        print("-" * 48)
        print(f"| {'MedID':<6} | {'Medname':<15} | {'Qty':<4} | {'Value':<10} |")
        print("-" * 48)
        for i in rec:
            print(f"| {i[0]:<6} | {i[1]:<15} | {i[2]:<4} | {i[3]:<10.2f} |")
        print("-" * 48)
        print("\t\t\t\t TOTAL=",grand_total)
        print("-" * 48)
        con.close()
        return render_template("display_sales_report.html",
                               rec=rec,
                               total=grand_total,
                               date=purchase_date
                               )
    return render_template("sales_report_form.html")

@app.route('/generate_bill',methods=['GET','POST'])
def generate_bill():
    if request.method=='POST':
        head="_"*90
        con=get_connection()
        cur=con.cursor()
        pur_date=request.form["pur_date"]
        customerid=request.form['customer_id']
        cur.execute(
           "select p.med_id,p.med_name,i.mfr,i.exp,p.qty,p.mrp,p.value from Purchase_History p join inventory i on p.med_id=i.med_id where p.p_date=%s and p.cust_id=%s",
            (pur_date,customerid)
        )
        result=cur.fetchall()
        cur.execute(
            "select name from customer where cust_id=%s",
            (customerid,)
        )
        result2=cur.fetchall()[0][0]
        cur.execute(
            "select sum(value) from Purchase_History where p_date=%s and cust_id=%s",
            (pur_date,customerid)
        )
        finalresult=cur.fetchone()[0]
        con.close()
        return render_template("display_bill.html",
                               pur_date=pur_date,
                               customerid=customerid,
                               Result=result,
                               Result2=result2,
                               Total=finalresult
                               )
    return render_template("display_bill_generate_form.html")

if __name__ == "__main__":
    app.run(debug=True)

