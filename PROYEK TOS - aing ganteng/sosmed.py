from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import sqlite3 as sql
import time
app = Flask(__name__)
app.secret_key = 'kappa123'
@app.route('/')
def home():
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("SELECT * FROM posts where points>=500 order by submitdate desc")
   rows = cur.fetchall()
   cur.execute("SELECT count(*) FROM posts where points>=500 order by submitdate desc")
   rowcount = cur.fetchone()[0]
   val=[]
   total=[]
   ownerimage=[]
   for row in rows:
      cur.execute("SELECT points from posts where id=?",(row["id"],))
      val.append(cur.fetchone()[0])
      cur.execute("select count(*) from comments where post_id=?",(row["id"],))
      total.append(cur.fetchone()[0])
      cur.execute("select image from user where username=?",(row["owner"],))
      ownerimage.append(cur.fetchone()[0])
   return render_template('home.html',rows = rows,val=val,total=total,ownerimage=ownerimage,rowcount = rowcount)

@app.route('/fresh')
def fresh():
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("SELECT * FROM posts where points<500 order by submitdate desc")
   rows = cur.fetchall()
   val=[]
   total=[]
   ownerimage=[]
   for row in rows:
      cur.execute("SELECT points from posts where id=?",(row["id"],))
      val.append(cur.fetchone()[0])
      cur.execute("select count(*) from comments where post_id=?",(row["id"],))
      total.append(cur.fetchone()[0])
      cur.execute("select image from user where username=?",(row["owner"],))
      ownerimage.append(cur.fetchone()[0])
   return render_template('fresh.html',rows = rows,val=val,total=total,ownerimage=ownerimage)

@app.route('/register')
def register():
   return render_template('register.html')

@app.route('/signin',methods = ['POST'])
def signin():
   if request.method == 'POST':
         username = request.form['uname']
         pwd = request.form['pw']
         success = '0'
         con = sql.connect("database.db")
         con.row_factory = sql.Row
         cur = con.cursor()
         cur.execute("select * from user where username=? and password=?",(username,pwd,))
         rows = cur.fetchone()
         cur.execute("select count(*) from user where username=? and password=?",(username,pwd,))
         rowcount = cur.fetchone()[0]
         if rowcount>0:
             session['username'] = rows['username']
             session['name'] = rows['fullname']
             session['image'] = rows['image']
             return "ok"
         else:
             return "invalid"

@app.route('/signup',methods = ['POST'])
def signup():
   if request.method == 'POST':
         con = sql.connect("database.db")
         cur = con.cursor()
         user = request.form['username']
         pwd = request.form['password']
         confirm = request.form['confirm']
         name = request.form['fullname']
         email = request.form['email']
         imageurl = request.form['image']
         if pwd == confirm:
            cur.execute("INSERT INTO user VALUES(?,?,?,?,?)",(user,pwd,name,email,imageurl,))
            con.commit()
            return redirect(url_for('home'))
         else:
            return redirect(url_for('register'))

@app.route('/usernamecheck', methods = ['POST'])
def usernamecheck():
   user = request.form['username']
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("SELECT COUNT(*) as jumlah from user where username=?",(user,))
   rows = cur.fetchone()[0]
   if rows == 0:
      return "200 OK"
   else:
      return "not available"

@app.route('/upload')
def upload():
   return render_template('upload.html')

@app.route('/submitpost',methods = ['POST'])
def submitpost():
   if request.method == 'POST':
      caption = request.form['caption']
      image = request.form['image']
      owner = session['username']
      date = time.strftime("%d/%m/%Y")
      con = sql.connect("database.db")
      cur = con.cursor()
      cur.execute("INSERT INTO posts VALUES(NULL,?,?,?,?,?)",(caption,image,owner,date,1,))
      con.commit()
      return redirect(url_for('myprofile'))

@app.route('/myprofile')
def myprofile():
   username = session['username']
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("SELECT COUNT(*) FROM posts where owner=?",(username,))
   totalposts = cur.fetchone()[0]
   cur.execute("SELECT SUM(points) FROM posts where owner=?",(username,))
   totalpoints = cur.fetchone()[0]
   if totalpoints == None:
      totalpoints = 0
   cur.execute("select * from posts where owner=?",(username,))
   rows = cur.fetchall()
   cur.execute("SELECT count(*) from posts where owner=?",(username,))
   rowcount = cur.fetchone()[0]
   val =[]
   total = []
   for row in rows:
      cur.execute("SELECT points from posts where id=?",(row["id"],))
      val.append(cur.fetchone()[0])
      cur.execute("select count(*) from comments where post_id=?",(row["id"],))
      total.append(cur.fetchone()[0])
   return render_template('myprofile.html',rows = rows,rowcount = rowcount,totalpoints = totalpoints,totalposts = totalposts,val=val,total=total)

@app.route('/logout')
def logout():
   session.pop('username', None)
   session.pop('name', None)
   session.pop('image', None)
   return redirect(url_for('home'))

@app.route('/viewprofile', methods = ['GET'])
def viewprofile():
   uname = request.args.get('username')
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("select * from user where username=?",(uname,))
   rows = cur.fetchone()
   cur.execute("SELECT COUNT(*) FROM posts where owner=?",(uname,))
   totalposts = cur.fetchone()[0]
   cur.execute("SELECT SUM(points) FROM posts where owner=?",(uname,))
   totalpoints = cur.fetchone()[0]
   if totalpoints == None:
      totalpoints = 0
   cur.execute("SELECT * FROM posts where owner=?",(uname,))
   posts = cur.fetchall()
   cur.execute("SELECT count(*) from posts where owner=?",(uname,))
   rowcount = cur.fetchone()[0]
   val = []
   total = []
   for row in posts:
      cur.execute("SELECT points from posts where id=?",(row["id"],))
      val.append(cur.fetchone()[0])
      cur.execute("select count(*) from comments where post_id=?",(row["id"],))
      total.append(cur.fetchone()[0])
   return render_template('viewprofile.html',rows = rows,posts = posts,totalposts=totalposts,totalpoints=totalpoints,rowcount=rowcount,val=val,total=total)

@app.route('/search', methods = ['GET'])
def search():
   key = request.args.get('key')
   array = []
   percent = '%'
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("select * from user where username LIKE ?",(percent+key+percent,))
   rows = cur.fetchall()
   for row in rows:
      array.append(row['username'])
   return jsonify(array)

@app.route('/result', methods = ['GET'])
def result():
   q = request.args.get('q')
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   percent = '%'
   cur = con.cursor()
   cur.execute("select * from user where username LIKE ?",(percent+q+percent,))
   rows = cur.fetchall()
   cur.execute("SELECT count(*) from user where username LIKE ?",(percent+q+percent,))
   rowcount = cur.fetchone()[0]
   return render_template('result.html',rows = rows,q = q,rowcount = rowcount)
   
@app.route('/postdetail', methods = ['GET'])
def postdetail():
   id = request.args.get('id')
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("select * from posts where id=?",(id))
   rows = cur.fetchone()
   cur.execute("select image from user where username=?",(rows["owner"],))
   ownerimage = cur.fetchone()[0]
   cur.execute("SELECT points from posts where id=?",(id,))
   val = cur.fetchone()[0]
   cur.execute("select count(*) from comments where post_id=?",(id,))
   total = cur.fetchone()[0]
   cur.execute("SELECT * FROM comments where post_id=? order by commentdate desc",(id,))
   res = cur.fetchall()
   cur.execute("SELECT count(*) from comments where post_id=?",(id,))
   rowcount = cur.fetchone()[0]
   image = []
   for re in res:
      cur.execute("SELECT image from user where username=?",(re['username'],))
      image.append(cur.fetchone()[0])
   return render_template('postdetail.html',rows = rows,res = res,rowcount = rowcount,val=val,total=total,image=image,ownerimage=ownerimage)

@app.route('/submitcomment', methods = ['POST'])
def submitcomment():
   if request.method == 'POST':
      username = session['username']
      comment = request.form['comment']
      postid = request.form['postid']
      date = time.strftime("%d/%m/%Y")
      con = sql.connect("database.db")
      cur = con.cursor()
      cur.execute("INSERT INTO comments VALUES (NULL,?,?,?,?)",(comment,postid,username,date,))
      con.commit()
      return ('', 204)

@app.route('/changepassword')
def changepassword():
   return render_template('changepassword.html')

@app.route('/deletepost', methods= ['POST'])
def deletepost():
   if request.method == 'POST':
      postid = request.form['idpost']
      con = sql.connect("database.db")
      cur = con.cursor()
      cur.execute("DELETE from posts where id=?",(postid,))
      cur.execute("DELETE from comments where post_id=?",(postid,))
      con.commit()
      return('',204)

@app.route('/deletecomment', methods= ['POST'])
def deletecomment():
   if request.method == 'POST':
      commentid = request.form['id']
      con = sql.connect("database.db")
      cur = con.cursor()
      cur.execute("DELETE from comments where id=?",(commentid,))
      con.commit()
      return('',204)

@app.route('/editprofile')
def editprofile():
   username = session['username']
   con = sql.connect("database.db")
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("select * from user where username =?",(username,))
   rows = cur.fetchone()
   return render_template('editprofile.html',rows = rows)

@app.route('/editpost', methods= ['GET'])
def editpost():
   con = sql.connect("database.db")
   pid = request.args.get('id')
   con.row_factory = sql.Row
   cur = con.cursor()
   cur.execute("select * from posts where id=?",(pid,))
   row = cur.fetchone()
   return render_template('editpost.html',row = row)

@app.route('/updatepassword', methods = ['POST'])
def updatepassword():
   if request.method == 'POST':
      username = session['username']
      oldpass = request.form['oldpass']
      passw = request.form['password']
      confirm = request.form['confirm']
      con = sql.connect("database.db")
      con.row_factory = sql.Row
      cur = con.cursor()
      cur.execute("select * from user where username =?",(username,))
      rows = cur.fetchone()
      if rows['password'] == oldpass and passw == confirm:
         cur.execute("UPDATE user SET password=? WHERE username=?",(passw,username,))
         con.commit()
         return "ok"
      else:
         return "wrong"


@app.route('/updateprofile', methods = ['POST'])
def updateprofile():
   if request.method == 'POST':
      username = session['username']
      fullname = request.form['fullname']
      email = request.form['email']
      img = request.form['image']
      con = sql.connect("database.db")
      cur = con.cursor()
      cur.execute("UPDATE user SET fullname=?,email=?,image=? where username=?",(fullname,email,img,username,))
      con.commit()
      session['name'] = fullname
      session['image'] = img
      return "ok"
   else:
      return "wrong"

@app.route('/updatepost', methods = ['POST'])
def updatepost():
   if request.method == 'POST':
      postid = request.form['postid']
      capt = request.form['caption']
      con = sql.connect("database.db")
      cur = con.cursor()
      cur.execute("UPDATE posts SET caption=? where id=?",(capt,postid,))
      con.commit()
      return redirect(url_for('postdetail',id=postid))
   else:
      return "wrong"



if __name__ == '__main__':
   app.debug = True
   app.run('0.0.0.0',5000)

