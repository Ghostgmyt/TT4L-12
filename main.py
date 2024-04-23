from flask import Flask , render_template

system = Flask(__name__)      

@system.route('/')
def login():
  
   return render_template('login.html')

'''if __name__ == '__main__':'''
system.run(debug=True)













    
