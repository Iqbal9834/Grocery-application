from flask import*
import os
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_mail import Message
import nexmo
UPLOAD_FOLDER = 'static/uploads'
app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME='iqbalali9554@gmail.com',
    MAIL_PASSWORD='ritu34@mojo'
)
client=nexmo.Client(key='47ee9d6f', secret='4KrBygGNe1RYnDMm')
mail=Mail(app)
bcrypt=Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///User.db'
app.config['SECRET_KEY'] = 'random string'    
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
db = SQLAlchemy(app)
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Items(db.Model):
    prdctname=db.Column(db.String(30), nullable=False)#0
    price=db.Column(db.Integer)#1
    catagory=db.Column(db.String(40), nullable=False)#2
    image=db.Column(db.String(30))#3
    descrptn=db.Column(db.String(130), nullable=False)#4
    quntity=db.Column(db.Integer, nullable=False)#5
    productId=db.Column(db.Integer,primary_key=True)#6
    cart=db.relationship('Cart', backref='Items', uselist=False)

class Login(db.Model):
    userid=db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    Name=db.Column(db.String(120), nullable=False)
    Email=db.Column(db.String(120), nullable=False)
    PhoneNumber=db.Column(db.Integer, nullable=False)
    Password=db.Column(db.String(80))
    cart=db.relationship('Cart', backref='Login', uselist=False)


class Cart(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    userid=db.Column(db.Integer, db.ForeignKey(Login.userid))
    productId=db.Column(db.Integer, db.ForeignKey(Items.productId), nullable=False)
    quantity=db.Column(db.Integer, nullable=False)

class Adress(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    # productid=db.Column(db.Integer, nullable=False,unique=True)
    StreetName=db.Column(db.String(100), nullable=False)
    City=db.Column(db.String(10),nullable=False)
    State=db.Column(db.String(10), nullable=False)
    Pincode=db.Column(db.Integer,nullable=False)
    LandMark=db.Column(db.String, nullable=True)
    Email=db.Column(db.String, nullable=False)

class Order(db.Model):
    orderid=db.Column(db.Integer,primary_key=True, nullable=False)
    productid=db.Column(db.Integer, nullable=False)
    address=db.Column(db.String, nullable=False)
    number=db.Column(db.Integer, nullable=False)
    price=db.Column(db.Integer, nullable=False)
    qty=db.Column(db.Integer, nullable=False)

def getUserInformation():
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            user=Login.query.filter_by(Email=session['email']).first()
            userId=user.userid
            noOfItems=Cart.query.filter_by(userid=userId).count()
            prducts=Cart.query.filter_by(userid=userId).all()
            totalprice=0
            for prduct in prducts:
                abc=prduct.productId
                quntity=Cart.query.filter_by(productId=abc).first()
                prc=quntity.quantity
                itm=Items.query.filter_by(productId=abc).first()
                totalprice+=itm.price*prc
        return (loggedIn, noOfItems, userId,totalprice)

# @app.route('/')
# def login():
#     return render_template('login.html')

@app.route('/link')
def link():
    division =(request.args.get('catagory'))
    if(division):
        items=Items.query.filter_by(catagory=division).all()
    else:
        items=Items.query.all()
    return render_template('link.html', items=items)

@app.route('/log', methods=['GET','POST'])
def log():
    if(request.method=='POST'):
        nm=request.form.get('username')
        ps=request.form.get('password')
        admin=Admin.query.filter_by(username=nm).first()
        result=bcrypt.check_password_hash(admin.password,ps)
        if(result):
             return render_template('home.html')
    else:
        return render_template('login.html')
    
@app.route('/log/show')
def Show_items():
    return render_template('Show.html',items=Items.query.all())

@app.route('/add',methods=['GET','POST'])
def add():
    if request.method=='POST':
        prdctn=request.form.get('pn')
        pric=request.form.get('prc')
        catgry=request.form.get('cty')
        descrpton=request.form.get('despon')
        quanity=request.form.get('qnty')

        image = request.files['img']
        name=secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER,name))
        item=Items(prdctname=prdctn, price=pric, catagory=catgry,image=name,descrptn=descrpton,quntity=quanity)
        db.session.add(item)
        db.session.commit()
        return render_template('Add_Item.html')
    else:
        return render_template('Add_Item.html')

@app.route('/')
def index():
    return render_template('doodwala.html', item=Items.query.all())

@app.route('/product')
def product():
    return render_template('product.html', item=Items.query.all())

@app.route('/Signin', methods=['GET','POST'])
def signin():
    if request.method=='POST':
        hashed =''
        user_name=request.form.get('name')
        user_email=request.form.get('email')
        user_number=request.form.get('number')
        user_paswrd=request.form.get('paswrd')
        hashed=bcrypt.generate_password_hash(user_paswrd).decode('utf8')
        users=Login(Name=user_name, Email=user_email, PhoneNumber=user_number,Password=hashed)
        db.session.add(users)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('Signin.html')

@app.route('/usrlog', methods=['GET','POST'])
def usrlog():
   if 'email' not in session:
       if(request.method=='POST'):
           nm=request.form.get('nme')
           ps=request.form.get('psrd')
           users=Login.query.filter_by(Name=nm).first()
           session['email'] = users.Email
           if bcrypt.check_password_hash(users.Password, ps):
               return redirect(url_for("index"))
           else:
               render_template('login.html')
       else:
           return render_template('userlogin.html')
   else:
       return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect(url_for('usrlog'))
    else:
        email=session['email']
        user=Login.query.filter_by(Email=email).first()
        usrname=user.Name
        usrphno=user.PhoneNumber
        usremail=user.Email
    return render_template('profile.html',usrname=usrname,usrphno=usrphno,usremail=usremail)

@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email',None)
        return render_template('doodwala.html')
    else:
        return render_template('doodwala.html')

@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('usrlog'))
    else:
        produtId =(request.args.get('produtId'))
        qun=1
        user=Login.query.filter_by(Email=session['email']).first()
        userId = user.userid
        if Cart.query.filter_by(userid=userId, productId=produtId).first():
            query=Cart.query.filter_by(userid=userId,productId=produtId).first()
            incremnt=query.quantity
            incremnt+=1
            query.quantity=incremnt
            db.session.commit()
            return redirect(url_for('link'))
        else:
            query=Cart(userid=userId, quantity=qun, productId=produtId)
            db.session.add(query)
            db.session.commit()
            return redirect(url_for('link'))
    # return redirect(url_for('cart'))

@app.route('/remove')
def remove():
    if 'email' not in session:
        return redirect(url_for('usrlog'))
    else:
        remove=[]
        produtId=request.args.get('produtId')
        print(produtId)
        loggedIn, noOfItems, usrid= getUserInformation()
        remove=Cart.query.filter_by(productId=produtId,userid=usrid).first()
        db.session.delete(remove)
        db.session.commit()
        return redirect(url_for('cart'))

@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('usrlog'))
    loggedIn, noOfItems, usrid, totalprice= getUserInformation()
    if noOfItems==0:
        return redirect(url_for('index'))
    else:
        prducts=Cart.query.filter_by(userid=usrid).all()
        itms=[]
        qun=[]
        qun.append(0)
        for prduct in prducts:
            abc=prduct.productId
            quntity=Cart.query.filter_by(productId=abc).first()
            prc=quntity.quantity
            qun.append(prc)
            print(prc)
            itm=Items.query.filter_by(productId=abc).first()
            itms.append(itm)
    print(itms)
    print(qun)
    return render_template("cart.html", itms = itms, noOfItems=noOfItems, totalprice=totalprice,qunty=qun)

@app.route('/downClick')
def downClick():
   produtId=request.args.get('produtId')
   print(produtId)
   loggedIn, noOfItems, usrid, totalprice= getUserInformation()
   query=Cart.query.filter_by(userid=usrid,productId=produtId).first()
   qun=query.quantity
   qun+=1
   query.quantity=qun
   print(qun)
   db.session.commit()
   return redirect(url_for('cart'))

@app.route('/upClick')
def upClick():
   produtId=request.args.get('produtId')
   loggedIn, noOfItems, usrid, totalprice= getUserInformation()
   query=Cart.query.filter_by(userid=usrid,productId=produtId).first()
   qun=query.quantity
   if(qun<=0):
       qun=0
       query.quantity=qun
   else:
        qun-=1
        query.quantity=qun
   print(qun)
   db.session.commit()
   return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    if 'email' not in session:
        return redirect(url_for('usrlog'))
    else:
        loggedIn, noOfItems, usrid, totalprice=getUserInformation()
        email=session['email']
        if(Adress.query.filter_by(Email=email)):
            return redirect(url_for('check'))
        else:
            user=Login.query.filter_by(Email=email).first() 
            return render_template('Personal.html',user=user,totalprice=totalprice)

@app.route('/gofurther', methods=['GET','POST'])
def gofurther():
    if (request.method=='POST'):
        Pincode=request.form.get('pincode')
        StreetName=request.form.get('StreetName')
        City=request.form.get('city')
        State=request.form.get('state')
        LandMark=request.form.get('landmark')
        Email=request.form.get('email')
        reference=Adress(StreetName=StreetName,State=State,City=City,LandMark=LandMark,Pincode=Pincode,Email=Email)
        db.session.add(reference)
        db.session.commit()
        return redirect(url_for('cart'))
    else:
        return redirect(url_for('checkout'))
@app.route('/check')
def check():
    if 'email' not in session:
        return redirect(url_for('usrlog'))
    else:
        email=session['email']
        loggedIn, noOfItems, usrid, totalprice= getUserInformation()
        adress=Adress.query.filter_by(Email=email).first()
        contact=Login.query.filter_by(Email=email).first()
        return render_template('checkout.html',adress=adress,contact=contact, noOfItems=noOfItems, totalprice=totalprice)
    return render_template('profile.html')

@app.route('/order')
def order():
    loggedIn, noOfItems, usrid, totalprice= getUserInformation()
    remove=Cart.query.filter_by(userid=usrid).all()
    for rm in remove:
        db.session.delete(rm)
    db.session.commit()
    # email=session['email']
    # mail.send_message('New message from'+'FreshOway',
    # sender='iqbalali9554@gmail.com',
    # recipients=['iqbalali9554@gmail.com'],
    # body='Your order has been successfully placed. Look outside because we deliver within a minute Lol!'
    #  )
    client.send_message({
    'from': 'FreshOway',
    'to': '919870340879',
    'text': 'Your order has been placed ',
    }) 
    return render_template('orderConfermation.html')

@app.route('/Cancel')
def Cancel():
    client.send_message({
        'from': 'FreshOway',
        'to': '919870340879',
        'text': 'Your order has been canceled',
        })
    return redirect(url_for('index'))

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/change')
def change():
    loggedIn, noOfItems, usrid, totalprice=getUserInformation()
    email=session['email']
    user=Login.query.filter_by(Email=email).first() 
    return render_template('Personal.html',user=user,totalprice=totalprice)


if __name__ == '__main__':
    app.run(debug=True)   
