from forms import ProjectForm, SignInForm, SignUpForm, TaskForm
from flask import Flask, render_template, request, flash, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Tien Python-Flask Web App'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()

db = SQLAlchemy(app)
migrate = Migrate(app, db)
import models

@app.route('/')
def main():
    todolist = [
        {
            'name': 'Buy milk',
            'description': 'Buy 2 liters of milk in Coopmart.'
        },
        {
            'name': 'Get money',
            'description': 'Get 500k from ATM'
        }
    ]
    return render_template('index.html', todolist = todolist)
    
@app.route('/signUp', methods=['GET', 'POST'])
def showSignUp():
    form = SignUpForm()
    if form.validate_on_submit():
        _fname = form.inputFirstName.data
        _lname = form.inputLastName.data
        _email = form.inputEmail.data
        _password = form.inputPassword.data

        if(db.session.query(models.User).filter_by(email=_email).count() == 0):
            #user = {'fname':_fname, 'lname':_lname,'email':_email,'password':_password}
            user = models.User(first_name = _fname, last_name = _lname, email = _email)
            user.set_password(_password)
            db.session.add(user)
            db.session.commit()
            return render_template('signUpSuccess.html', user=user)
        else:
            flash('Email {} is already exists!'.format(_email))
            return render_template('signup.html', form = form)


    return render_template('signup.html', form = form)

@app.route('/signIn', methods=['GET', 'POST'])
def signin():
    form = SignInForm()

    if form.validate_on_submit():
        _email = form.inputEmail.data
        _password = form.inputPassword.data

        user = db.session.query(models.User).filter_by(email=_email).first()
        if (user is None):
            flash('Wrong email address or password!')
        else:
            if (user.check_password(_password)):
                session['user'] = user.user_id
                #return render_template('userhome.html')
                return redirect('/listProject')
            else:
                flash('Wrong email address or password!')
    return render_template('signin.html', form = form)
    
# @app.route('/userHome', methods=['GET', 'POST'])
# def userHome():
#     _user_id = session.get('user')
#     if _user_id:
#         user = db.session.query(models.User).filter_by(user_id=_user_id).first()
#         return render_template('userhome.html', user = user)
#     else:
#         return redirect('/')
@app.route('/listTask', methods=['GET', 'POST'])
def listTask():
    _user_id = session.get('user')
    tasks = db.session.query(models.Task)
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        lsTask = db.session.query(models.Task)
        return render_template('listTask.html',user=user,lsTask=lsTask)
    else:
        return redirect('/')
@app.route('/newTask', methods=['GET', 'POST'])
def newTask():
    _user_id = session.get('user')
    form = TaskForm()
    form.inputPriority.choices = [(p.priority_id, p.text) for p in db.session.query(models.Priority).all()] 
  
    form.inputStatus.choices = [(p.status_id, p.description) for p in db.session.query(models.Status).all()] 
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        _project_id = request.form['hiddenProjectTaskId'] 
        project = db.session.query(models.Project).filter_by(project_id =_project_id).first()
        if form.validate_on_submit():
           
            _description = form.inputDescription.data
            _deadline = form.inputDeadline.data
            _priority_id = form.inputPriority.data
          
            project = db.session.query(models.Project).filter_by(project_id =_project_id).first()
            _status_id = form.inputStatus.data
            priority = db.session.query(models.Priority).filter_by(priority_id =_priority_id).first()
            project = db.session.query(models.Project).filter_by(project_id =_project_id).first()
            status = db.session.query(models.Status).filter_by(status_id =_status_id).first()
            _task_id = request.form['hiddenTaskId']
            tasks = db.session.query(models.Task).filter_by(project=project).all()
            if (_task_id == "0"):
                if  _deadline < project.deadline:
                    status = db.session.query(models.Status).first()
                    task = models.Task(description = _description, deadline = _deadline, priority = priority,project = project,status=status)
                    db.session.add(task)
                else:
                    flash("Task's deadline must not be after project's deadline")
                    return render_template('/newtask.html', form = form, user = user,project_id=_project_id)
            else:
                task = db.session.query(models.Task).filter_by(task_id = _task_id).first()
                task.description = _description
                task.deadline = _deadline
                task.priority = priority
                
                task.status = status
                editProject = db.session.query(models.Project).filter_by(project_id = task.project.project_id).first()
                
                lsTaskNotDone = db.session.query(models.Task).filter_by(project_id=_project_id,status_id=4).all()
                lsTaskLate = db.session.query(models.Task).filter_by(project_id=_project_id,status_id=3).all()
                lsTaskNot = db.session.query(models.Task).filter_by(project_id=_project_id,status_id=1).all()
               
                if len(lsTaskLate)==0:
                    if len(lsTaskNot)==len(tasks):
                        getProject = db.session.query(models.Project).filter_by(project_id=_project_id).first()
                        getProject.status_id = 1
                    if len(lsTaskNotDone)==len(tasks):
                        getProject = db.session.query(models.Project).filter_by(project_id=_project_id).first()
                        getProject.status_id = task.status_id
                    else:
                        getProject = db.session.query(models.Project).filter_by(project_id=_project_id).first()
                        getProject.status_id = 2
                    if task.status.description=='Đang thực hiện':
                        editProject.status = status
                if task.status.description=='Quá hạn':
                    editProject.status = status
                
                
            
            db.session.commit()
            lstasks = db.session.query(models.Task).filter_by(project=project).all()
            return render_template('listTask.html',user=user,lsTask=lstasks,project_id=_project_id)

        return render_template('/newtask.html', form = form, user = user,project_id=_project_id)
    
    return redirect('/')
@app.route('/listProject', methods=['GET', 'POST'])
def listProject():
   
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        lsProject = db.session.query(models.Project).filter_by(user=user).all()
        return render_template('listProject.html',user=user,lsProject=lsProject)
    return ('/')
@app.route('/searchProject', methods=['GET', 'POST'])
def searchProject():
   
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
       
        _search_project = request.form['searchProjectId']
        status = db.session.query(models.Status).filter_by(description=_search_project).first()
        lsProject = db.session.query(models.Project).filter_by(name=_search_project,user=user).all()
        lsProject = lsProject + db.session.query(models.Project).filter_by(status=status,user=user).all()
        return render_template('listProject.html',user=user,lsProject=lsProject)
    return ('/')
@app.route('/searchTask', methods=['GET', 'POST'])
def searchTask():
   
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        _project_id = request.form['hiddenProjectTaskId']
        _search_task = request.form['searchTaskId']
        status = db.session.query(models.Status).filter_by(description=_search_task).first()
        lsTask = db.session.query(models.Task).filter_by(description=_search_task,project_id=_project_id).all()
        lsTask = lsTask + db.session.query(models.Task).filter_by(status=status,project_id=_project_id).all()
        return render_template('listTask.html',user=user,lsTask=lsTask,project_id=_project_id)
    return ('/')
@app.route('/newProject', methods=['GET', 'POST'])
def newProject():
    _user_id = session.get('user')
    form = ProjectForm()
    form.inputStatus.choices = [(p.status_id, p.description) for p in db.session.query(models.Status).all()] 
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        
        if form.validate_on_submit():
            _name = form.inputName.data
            _description = form.inputDescription.data
            _deadline = form.inputDeadline.data
            _status_id = form.inputStatus.data
            status = db.session.query(models.Status).filter_by(status_id= _status_id).first()
            
            _project_id = request.form['hiddenProjectId']
            if (_project_id == "0"):
                project = models.Project(name = _name, description = _description,deadline = _deadline, user = user, status = status)
                db.session.add(project)
            else:
                project = db.session.query(models.Project).filter_by(project_id = _project_id,user_id=_user_id).first()
                project.name = _name
                project.description = _description
                project.deadline = _deadline
                
                 
            db.session.commit()
            return redirect('/listProject')

        return render_template('/newProject.html', form = form, user = user)
    
    return redirect('/')
@app.route('/deleteProject', methods=['GET', 'POST'])
def deleteProject():
    _user_id = session.get('user')
    if _user_id:
        _project_id = request.form['hiddenProjectId']        
        if _project_id:
            project = db.session.query(models.Project).filter_by(project_id=_project_id).first()
            db.session.delete(project)
            db.session.commit()
        return redirect('/listProject')        

    return redirect('/')
@app.route('/editProject', methods=['GET', 'POST'])
def editProject():
    _user_id = session.get('user')
    form = ProjectForm()
    form.inputStatus.choices = [(p.status_id, p.description) for p in db.session.query(models.Status).all()] 
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        _project_id = request.form['hiddenProjectId']
        if _project_id:
            project = db.session.query(models.Project).filter_by(project_id=_project_id).first()
            form.inputName.default = project.name
            form.inputDescription.default = project.description
            form.inputDeadline.default = project.deadline
            form.inputStatus.default = project.status_id
            form.process()
            
            return render_template('/newProject.html', form = form, user = user, project = project)
    
    return redirect('/')


@app.route('/deleteTask', methods=['GET', 'POST'])
def deleteTask():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        _task_id = request.form['hiddenTaskId']        
        if _task_id:
            task = db.session.query(models.Task).filter_by(task_id=_task_id).first()
            _projectId= task.project_id
            db.session.delete(task)
            db.session.commit()
        lsTask = db.session.query(models.Task).filter_by(project_id=_projectId).all()
        return render_template('listTask.html',user=user,lsTask=lsTask,project_id=_projectId)
    
    return redirect('/')

@app.route('/editTask', methods=['GET', 'POST'])
def editTask():
    _user_id = session.get('user')
    form = TaskForm()
   
    form.inputPriority.choices = [(p.priority_id, p.text) for p in db.session.query(models.Priority).all()] 
    form.inputStatus.choices = [(p.status_id, p.description) for p in db.session.query(models.Status).all()]
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        _task_id = request.form['hiddenTaskId']
        
        if _task_id:
            task = db.session.query(models.Task).filter_by(task_id=_task_id).first()
            form.inputDescription.default = task.description
            form.inputDeadline.default = task.deadline
            form.inputPriority.default = task.priority_id
            
            form.inputStatus.default = task.status_id
            form.process()
            return render_template('/newtask.html', form = form, user = user, task = task,project_id=task.project_id)
    
    return redirect('/')

@app.route('/doneTask', methods=['GET', 'POST'])
def doneTask():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        _task_id = request.form['hiddenTaskId']
      
        if _task_id:
            task = db.session.query(models.Task).filter_by(task_id=_task_id).first()
            status = db.session.query(models.Status).filter_by(description='Hoàn thành').first()
            task.status = status
            _projectId= task.project_id
         
            db.session.commit()
            lsTask = db.session.query(models.Task).filter_by(project_id=_projectId).all()
            lsTaskNotDone = db.session.query(models.Task).filter_by(project_id=_projectId,status_id=4).all()
            lsTaskLate = db.session.query(models.Task).filter_by(project_id=_projectId,status_id=3).all()
            if len(lsTaskLate)==0:
                if len(lsTaskNotDone)==len(lsTask):
                    getProject = db.session.query(models.Project).filter_by(project_id=_projectId).first()
                    getProject.status_id = task.status_id
                else:
                    getProject = db.session.query(models.Project).filter_by(project_id=_projectId).first()
                    getProject.status_id = 2
            
            db.session.commit()
            return render_template('listTask.html',user=user,lsTask=lsTask,project_id=_projectId)
    

    return redirect('/')
@app.route('/taskProject', methods=['GET', 'POST'])
def taskProject():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id=_user_id).first()
        project_id = request.form['hiddenProjectId']
        if project_id:
            task = db.session.query(models.Task).filter_by(project_id=project_id).all() 
            return render_template('listTask.html',user=user,lsTask=task,project_id=project_id)

        return redirect('/')
    
    return redirect('/')

if __name__ == '__main__':
    app.run(host='127.0.0.1',port='8080', debug=True)
